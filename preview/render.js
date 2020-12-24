globalThis.treeShowDelayMs = 250;

function createShader(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  const success = gl.getShaderParameter(shader, gl.COMPILE_STATUS);
  if (success) {
    return shader;
  }

  console.log(gl.getShaderInfoLog(shader));
  gl.deleteShader(shader);
}

function loadVertices() {
  const text = document.querySelector('pre.coords').textContent;
  const lines = text.split(/\n/g).filter(Boolean).map(line => JSON.parse(line));

  const vertices = new Float32Array(lines.length * 3);
  for (let i = 0; i < lines.length; ++i) {
    const offset = i * 3;
    vertices[offset + 0] = lines[i][1] * 0.005;
    vertices[offset + 1] = lines[i][2] * 0.005;
    vertices[offset + 2] = lines[i][0] * 0.005;
  }

  return vertices;
}

/**
 * @param {string} source
 * @param {AbortSignal} abortSignal
 */
async function runCurrentScript(source, abortSignal) {
  let shouldRun = true;

  function interruptHandler(susp) {
    if (shouldRun !== true) {
      throw new Error('interrupt');
    }
    return null;
  }

  abortSignal.addEventListener('abort', () => {
    shouldRun = false;
  });

  try {
    await Sk.misceval.asyncToPromise(() => {
      return Sk.importMainWithBody("<stdin>", false, source, true);
    }, {"*": interruptHandler});
  } catch (e) {
    if (e.message !== 'interrupt') {
      console.log(e);
    }
  }
}

async function runProgram() {
  /**
   * Load initial data:
   */
  const coordsSource = await fetch('../coords.txt').then(res => res.text());
  document.querySelector('pre.coords').textContent = coordsSource + '\n';

  if (location.hash.length > 1) {
    document.getElementById('source').textContent = atob(location.hash.slice(1));
  } else {
    const spinSource = await fetch('../xmaslights-spin.py')
      .then(res => res.text());
    document.getElementById('source').textContent = spinSource + '\n';
  }

  const editor = CodeMirror.fromTextArea(document.getElementById('source'), {
    lineNumbers: true,
    mode: 'python',
  });

  const vertices = loadVertices();

  /** @type {HTMLCanvasElement} */
  const preview = document.getElementById('preview');
  const gl = preview.getContext('webgl');
  gl.enable(gl.DEPTH_TEST);
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

  const program = gl.createProgram();
  {
    const vertexShaderSource = document.getElementById('vshader').text;
    const fragmentShaderSource = document.getElementById('fshader').text;
    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    gl.bindAttribLocation(program, 0, 'pos');
    gl.bindAttribLocation(program, 1, 'colorIn');
  }
  gl.useProgram(program);

  /**
   * @param {Uint8Array} colors
   */
  function renderPixels(colors) {
    gl.viewport(0, 0,
      gl.drawingBufferWidth, gl.drawingBufferHeight);
    gl.clearColor(0.05, 0.05, 0.05, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);

    const colorOffset = vertices.byteLength;

    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, colorOffset + colors.byteLength, gl.STATIC_DRAW);
    gl.bufferSubData(gl.ARRAY_BUFFER, 0, vertices);
    gl.bufferSubData(gl.ARRAY_BUFFER, colorOffset, colors);

    const verticesLoc = gl.getAttribLocation(program, 'pos');
    gl.vertexAttribPointer(verticesLoc, 3, gl.FLOAT, false, 0, 0);
    gl.enableVertexAttribArray(verticesLoc);
    const colorsLoc = gl.getAttribLocation(program, 'colorIn');
    gl.vertexAttribPointer(colorsLoc, 4, gl.UNSIGNED_BYTE, true, 0, colorOffset);
    gl.enableVertexAttribArray(colorsLoc);

    const locPointSize = gl.getUniformLocation(program, 'pointSize');
    gl.uniform1f(locPointSize, 2.0);
    gl.drawArrays(gl.POINTS, 0, vertices.length / 3);

    gl.deleteBuffer(buffer);
  }
  globalThis.renderPixels = renderPixels;

  Sk.builtinFiles.files['src/builtin/board.py'] = `
D18 = 'D18'
`;

  Sk.builtinFiles.files['src/lib/neopixel.js'] = `
var $builtinmodule = ${function () {
  const mod = {__name__: new Sk.builtin.str('neopixel')};
  mod.__file__ = 'src/lib/neopixel.js';
  mod.__package__ = new Sk.builtin.str('');

  mod.NeoPixel = Sk.misceval.buildClass(mod, ($gbl, $loc) => {
    function initNeoPixel(kwargs, self, pin, pixelCount) {
      self.pin = pin;
      self.pixelCount = pixelCount;
      // console.log({kwargs});
      // self.autoWrite = kwargs['auto_write'] ?? false;
      self.pixels = new Uint8Array(Sk.ffi.remapToJs(pixelCount) * 4);
    }
    initNeoPixel['co_kwargs'] = true;
    $loc.__init__ = new Sk.builtin.func(initNeoPixel);

    $loc.__setitem__ = new Sk.builtin.func((self, offset, value) => {
      const [r, g, b] = Sk.ffi.remapToJs(value);
      const scaledOffset = Sk.ffi.remapToJs(offset) * 4;
      self.pixels[scaledOffset + 1] = r;
      self.pixels[scaledOffset + 0] = g;
      self.pixels[scaledOffset + 2] = b;
      self.pixels[scaledOffset + 3] = 255; // alpha
      return value;
    });

    $loc.show = new Sk.builtin.func((self) => {
      return new Sk.misceval.promiseToSuspension((async () => {
        return new Promise((resolve) => {
          renderPixels(self.pixels);
          // TODO: Maybe use animation frame..?
          Sk.setTimeout(() => {
            resolve(Sk.builtin.none.none$);
          }, treeShowDelayMs);
        });
      })());
    });
  }, 'NeoPixel', []);

  return mod;
}};`;

  Sk.onAfterImport = (library) => {
    switch (library) {
      case 're': {
        // HACK: Get support for re.sub
        const re = Sk.sysmodules.entries.re.rhs.$d;
        re.sub = new Sk.builtin.func((pattern, replacement, original) => {
          const patternStr = Sk.ffi.remapToJs(pattern);
          const replStr = Sk.ffi.remapToJs(replacement);
          const originalStr = Sk.ffi.remapToJs(original);
          // TODO: Do this properly, maybe using other re.* things.
          const regex = new RegExp(patternStr, 'g');
          return new Sk.builtin.str(originalStr.replace(regex, replStr));
        });
        break;
      }
    }
  };

  Sk.pre = 'output';
  Sk.configure({
    output: (text) => {
      console.log(text);
    },
    read: (filename) => {
      if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][filename] === undefined) {
        // console.log('not found', filename, Sk.builtinFiles);
        throw "File not found: '" + filename + "'";
      }
      let fileContents = Sk.builtinFiles["files"][filename];

      return fileContents;
    },
  });

  editor.on('change', () => {
    const currentSource = editor.getValue();
    const base64 = btoa(currentSource);
    location.hash = base64;
  });

  /**
   * @type {AbortController|null}
   */
  let lastAbort = null;

  async function handleRunButtonClick() {
    if (lastAbort !== null) {
      lastAbort.abort();
    }

    const abort = new AbortController();
    lastAbort = abort;

    await runCurrentScript(editor.getValue(), abort.signal);
  }

  handleRunButtonClick();

  document.getElementById('play-btn').addEventListener('click', (e) => {
    handleRunButtonClick();
  });
}
runProgram();
