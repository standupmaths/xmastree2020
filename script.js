var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 1000 );

var renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );

fetch('./coords.txt')
  .then(response => {
      return response.text()
   })
   .then(t => {
       return t.split(/\n|\r/g)
        .filter(e => e.length > 0)
        .map(el => JSON.parse(el))
   })
  .then(data => {
      prepareScere(data);
      animate()
  });

var prepareScere = function (data) {
    data.forEach(([x, y, z]) => {
        var geometry = new THREE.SphereGeometry(10);
        geometry.translate(x, y, z);
        var material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
        var sphere = new THREE.Mesh( geometry, material );
        scene.add( sphere );
    })
}

camera.position.y = -800;
camera.rotation.x = Math.PI/2;
let r = 800;
let angle = 0;

var animate = function () {
	requestAnimationFrame( animate );
  
	angle += 0.02;
    
    camera.position.y = r * Math.cos(angle) * -1;
    camera.position.x = r * Math.sin(angle);
    camera.rotation.y = angle;

	renderer.render( scene, camera );
};