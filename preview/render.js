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

  return lines;
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


  const coordsSource = await fetch('../coords.txt')
    .then(res => res.text())

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
  

  var scene = new THREE.Scene();
  scene.background = new THREE.Color( 0x0 );
  var camera = new THREE.PerspectiveCamera( 75, preview.clientWidth/preview.clientHeight, 0.1, 2000 );

  var renderer = new THREE.WebGLRenderer();

  const controls = new OrbitControls( camera, preview );
  
  renderer.setSize( preview.clientWidth, preview.clientHeight );
  preview.appendChild( renderer.domElement );

  // Auto resize preview renderer.
  const resizeObserver = new ResizeObserver(entries => {
    preview.width = preview.clientWidth
    preview.height = preview.clientHeight
    renderer.setSize( preview.clientWidth, preview.clientHeight );
  });
  resizeObserver.observe( preview );

  //camera.position.y = -800;
  //camera.rotation.x = Math.PI/2;
  camera.position.set(-800, 480, 140)
  controls.update();
  controls.autoRotate = true;
  
  var maxBrightness = 50;
  controls.autoRotateSpeed = -2;

  

  vertices.forEach(([x, z, y]) => {
    var geometry = new THREE.SphereGeometry(3);
    geometry.translate(x, y, z);
    var material = new THREE.MeshBasicMaterial( { color: 0x000000 } );
    var sphere = new THREE.Mesh( geometry, material );
    scene.add( sphere );
  })

  const material = new THREE.LineBasicMaterial({
    color: 0x00FF00
  });
  for (var i = 0; i < 7; i++) {
    const points = [];
    points.push( new THREE.Vector3( -300, -450, i*100 - 300 ) );
    points.push( new THREE.Vector3( 300, -450, i*100 - 300 ) );

    const geometry = new THREE.BufferGeometry().setFromPoints( points );

    const line = new THREE.Line( geometry, material.clone() );
    scene.add( line );
  }

  for (var i = 0; i < 7; i++) {
    const points = [];
    points.push( new THREE.Vector3( i*100 - 300, -450,  -300) );
    points.push( new THREE.Vector3( i*100 - 300, -450, 300 ) );

    const geometry = new THREE.BufferGeometry().setFromPoints( points );

    const line = new THREE.Line( geometry, material.clone() );
    scene.add( line );
  }
  

  var animate = function () {
    requestAnimationFrame( animate );

    controls.update();
  
    renderer.render( scene, camera );
  };

  animate();

  let lastColors = new Uint8Array(500 * 4);

  let angleZ = 0;

  /**
   * @param {Uint8Array} colors
   */
  function renderPixels(colors) {
    lastColors = colors;
    colors.forEach(({r,g,b}, i) => {
      let { material } = scene.children[i];
      
      if(material) {

        material.color.setRGB(r/maxBrightness, g/maxBrightness, b/maxBrightness)
        material.needsUpdate = true;
      }

    })
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
      self.pixels = new Array(Sk.ffi.remapToJs(pixelCount));
    }
    initNeoPixel['co_kwargs'] = true;
    $loc.__init__ = new Sk.builtin.func(initNeoPixel);

    $loc.__setitem__ = new Sk.builtin.func((self, offset, value) => {
      const [g, r, b] = Sk.ffi.remapToJs(value);
      const scaledOffset = Sk.ffi.remapToJs(offset);
      
      self.pixels[scaledOffset] = { r, g, b };
      
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

  let shouldRotate = false;
  document.getElementById('rotate-check').addEventListener('change', (e) => {
    
    let { target: { checked }} = e;

    controls.autoRotate = checked;
    
  });

  document.getElementById('rotation-speed').addEventListener('change', (e) => {
    
    let { target: { value }} = e;

    controls.autoRotateSpeed = Number(value)
    
  });

  document.getElementById('max-brightness').addEventListener('change', (e) => {
    
    let { target: { value }} = e;

    maxBrightness = Number(value)
  });

  document.getElementById('background-color').addEventListener('change', (e) => {
    
    let { target: { value }} = e;
    //debugger;
    scene.background.setHex(parseInt(value.replace("#", "0x")))
  });

  document.getElementById('play-btn').addEventListener('click', (e) => {
    handleRunButtonClick();
  });
}
runProgram();
