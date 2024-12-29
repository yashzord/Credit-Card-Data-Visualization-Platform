import * as THREE from "https://threejs.org/build/three.module.js";
import { OrbitControls } from "./OrbitControls.js";

// Create a scene
const scene = new THREE.Scene();

// Create a camera
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
const cameraStartPositionY = 212; // Adjust this value to change the vertical position of the camera
// const cameraEndPositionY = 2; // Adjust this value to change the vertical position of the camera at the end

camera.position.set(0, cameraStartPositionY, 2500); // Adjust the camera position to start more zoomed out and above the planets
camera.rotation.x = -Math.PI / 3; // Adjust the camera rotation to look below the planets

// camera.position.set(0, 20, 200); // Adjust the camera position
// camera.rotation.x = -Math.PI / 6; // Adjust the camera rotation

// Create a renderer
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x000000); // Set clear color to black
document.body.appendChild(renderer.domElement);

// Create a container element for the welcome message
const welcomeContainer = document.createElement("div");
welcomeContainer.innerHTML = "Welcome to CoreCARD Visualization";
welcomeContainer.style.position = "absolute";
welcomeContainer.style.top = "-50px"; // Start offscreen
welcomeContainer.style.left = "50%";
welcomeContainer.style.transform = "translateX(-50%)"; // Center horizontally
welcomeContainer.style.padding = "10px";
welcomeContainer.style.fontSize = "2em";
welcomeContainer.style.fontFamily = "'FF Tisa Sans', sans-serif";
welcomeContainer.style.color = "white";
welcomeContainer.style.textShadow = "2px 2px 4px rgba(0, 0, 0, 0.5)"; // Set background color to white with transparency
welcomeContainer.style.transition = "top 1s"; // Set up a 2-second transition on the "top" property
document.body.appendChild(welcomeContainer);

// Start the animation after 1 second
setTimeout(() => {
  welcomeContainer.style.top = "50px"; // Move to 50px from the top
}, 1000);

// Create a container element for the menu
const menuContainer = document.createElement("div");
menuContainer.style.position = "absolute";
menuContainer.style.top = "10px";
menuContainer.style.left = "10px";
menuContainer.style.padding = "10px";
menuContainer.style.backgroundColor = "rgba(255, 255, 255, 0.8)"; // Set background color to white with transparency
menuContainer.style.fontFamily = "'FF Tisa Sans', sans-serif";
document.body.appendChild(menuContainer);

// Create the particle system
const particleCount = 500;
const particles = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);

for (let i = 0; i < particleCount * 3; i += 3) {
  positions[i] = Math.random() * 2000 - 1000;
  positions[i + 1] = Math.random() * 2000 - 1000;
  positions[i + 2] = Math.random() * 2000 - 1000;
}

particles.setAttribute("position", new THREE.BufferAttribute(positions, 3));
const particleMaterial = new THREE.PointsMaterial({
  color: 0xffffff,
  size: 2,
  // emissive: 0xffffff, // This will make the particles glow
  // emissiveIntensity: 5, // Adjust this value to increase or decrease the glow
});

const particleSystem = new THREE.Points(particles, particleMaterial);
scene.add(particleSystem);

// Create planets
const bigPlanetIds = [
  "TranType",
  "PrimaryCurrencyCode",
  "MessageTypeIdentifier",
  "ProcCode",
  "PhysicalSource",
  "MerchantGroup",
];
const smallPlanetIds = [
  "TransactionAmount",
  "OutstandingAmount",
  "CurrentBalance",
  "TotalOutStgAuthAmt",
  "CalcOTB",
  "priority",
];
const planets = [];
const moons = [];

const layoutRadius = 10; // Radius of the circular formation
const numPlanets = 6; // Number of big planets
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function updateRendererSize() {
  const width = window.innerWidth;
  const height = window.innerHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

window.addEventListener("resize", () => {
  updateRendererSize();
});

function onMouseClick(event) {
  // Calculate normalized device coordinates
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  // Raycast from the camera through the mouse coordinates
  raycaster.setFromCamera(mouse, camera);

  // Perform intersection check with small planets
  const smallPlanetIntersects = raycaster.intersectObjects(moons, true);

  if (smallPlanetIntersects.length > 0) {
    const clickedObject = smallPlanetIntersects[0].object;
    const bigPlanetId = clickedObject.parent.parent.userData.bigPlanetId;
    const smallPlanetId = clickedObject.userData.id;

    const clickData = {
      categorical_variable: bigPlanetId,
      numerical_variable: smallPlanetId,
    };
    sendClickData(clickData);
    console.log(localStorage.getItem("click-data-store"));

    return;
  }

  // Perform intersection check with big planets
  const bigPlanetIntersects = raycaster.intersectObjects(planets, true);

  if (bigPlanetIntersects.length > 0) {
    const clickedObject = bigPlanetIntersects[0].object;
    const bigPlanetId = clickedObject.userData.bigPlanetId;

    if (bigPlanetId === 'POS_entrymode') {
        const clickData = {
          categorical_variable: bigPlanetId,
        };
        sendClickData(clickData);
    }
    return;
  }
}

// Attach click event listener to the document
document.addEventListener("click", onMouseClick, false);

// Function to create and add a label to a planet
function createLabel(text) {
  const labelCanvas = document.createElement("canvas");
  const labelContext = labelCanvas.getContext("2d");
  const fontSize = 20;
  const fontFace = "'FF Tisa Sans', sans-serif";
  labelContext.font = `${fontSize}px ${fontFace}`;
  const textMetrics = labelContext.measureText(text);
  const textWidth = textMetrics.width;
  const textHeight = fontSize*1.2; // Use the font size for text height
  labelCanvas.width = textWidth;
  labelCanvas.height = textHeight;
  labelContext.font = `${fontSize}px ${fontFace}`;
  labelContext.fillStyle = "white";
  // Clear the canvas before drawing
  labelContext.clearRect(0, 0, labelCanvas.width, labelCanvas.height);
  // Adjust the y-coordinate to start the text from the baseline
  labelContext.fillText(text, 0, fontSize);
  const labelTexture = new THREE.CanvasTexture(labelCanvas);
  labelTexture.minFilter = THREE.LinearFilter;
  const labelMaterial = new THREE.SpriteMaterial({ map: labelTexture });
  const labelSprite = new THREE.Sprite(labelMaterial);
  // Adjust the scale and y-coordinate of the labelSprite
  labelSprite.scale.set(textWidth / 40, fontSize / 40, 1);
  labelSprite.position.set(0, 3 + fontSize / 80, 0); // Adjust the y-coordinate
  return labelSprite;
}

const newPlanet = new THREE.Mesh(
  new THREE.TorusKnotGeometry(0.5, 0.4, 66, 14, 7, 20), // TorusKnot
  new THREE.MeshStandardMaterial({ color: Math.random() * 0xffffff })
);

newPlanet.userData.bigPlanetId = 'POS_entrymode'; // Assign the new category

// Position the new planet at the center of the existing planet-moon system
newPlanet.position.set(0, 0, 0);

scene.add(newPlanet);
planets.push(newPlanet);

const newLabel = createLabel('POS_entrymode');
newPlanet.add(newLabel);

const planetGeometries = [
  new THREE.DodecahedronGeometry(1, 0),    // Dodecahedron
  new THREE.CylinderGeometry(1, 1, 1), // Cylinder
  new THREE.OctahedronGeometry(1, 0),    // Octahedron
  new THREE.TorusGeometry(1, 0.3, 16, 100), // Torus
  new THREE.IcosahedronGeometry(1, 0), // Icosahedron
  new THREE.TetrahedronGeometry(1, 0)  // Tetrahedron
];

const textureLoader = new THREE.TextureLoader();

// Define an array of URLs for the 6 textures
const textureURLs = [
  "https://media.istockphoto.com/id/1355640075/photo/cluster-of-golden-quartz-mineral-crystals.jpg?s=2048x2048&w=is&k=20&c=SlLR0N-u1CB5t-DEYY-92KrGv2GA2uV9TBttuSG8tKE=",
  "https://media.istockphoto.com/id/1330892321/photo/red-jewels.jpg?s=612x612&w=0&k=20&c=PR4168g-l544PJeTE8P3bJKbD7jB8IpcEWqao8m0iuE=",
  "https://media.istockphoto.com/id/990183542/photo/diamond-texture-closeup-and-kaleidoscope-top-view-of-round-gemstone-3d-render-3d-illustration.jpg?s=612x612&w=0&k=20&c=ir3_W3ygvQMq_C6ymuNFT0r7FgrYUHx2qVHX8Z5DQ8c=",
  "https://p0.pxfuel.com/preview/255/443/706/pebbles-crystals-acrylic-violet.jpg",
  "https://media.istockphoto.com/id/1285488881/vector/abstract-background-texture-of-golden-glitter.jpg?s=612x612&w=0&k=20&c=LsIxy2PO7NPFBbCwLWuOxPKRBp0lD39K4IRvzWLLBMM=",
  "https://as2.ftcdn.net/v2/jpg/03/03/85/23/1000_F_303852309_PnDlqRxgiNbOzBJqF28NY6BVLVPOmPr1.jpg"
];

// Load the textures into an array
const textures = textureURLs.map(url => textureLoader.load(url));

// Shuffle the textures array
for (let i = textures.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1));
  [textures[i], textures[j]] = [textures[j], textures[i]];
}

//planet loop creater
for (let i = 0; i < numPlanets; i++) {
  const angle = (i / numPlanets) * Math.PI * 2; // Calculate the angle for each planet
  const planetGeometry = planetGeometries[i % planetGeometries.length];
  const texture = textures[i % textures.length];
  const planet = new THREE.Mesh(
    planetGeometry,
    new THREE.MeshStandardMaterial({ map: texture })
  );

  planet.userData.bigPlanetId = bigPlanetIds[i]; // Assign corresponding big planet IDs

  const x = Math.cos(angle) * layoutRadius; // Calculate the x-coordinate on the circle
  const z = Math.sin(angle) * layoutRadius; // Calculate the z-coordinate on the circle

  planet.position.set(x, 0, z); // Set the position on the circle

  scene.add(planet);
  planets.push(planet);

  const moonGroup = new THREE.Group();
  planet.add(moonGroup);

  const radius = 2; // Radius of the moon's orbit
  const angleIncrement = (2 * Math.PI) / 6; // Angle increment between each moon

  for (let j = 0; j < 6; j++) {
    const angle = j * angleIncrement;

    const moon = new THREE.Mesh(
      new THREE.SphereGeometry(0.3, 16, 16),
      new THREE.MeshStandardMaterial({ color: Math.random() * 0xffffff })
    );
    moon.userData.id = smallPlanetIds[j]; // Assign small planet IDs cyclically

    // Set the position based on the radius and angle
    moon.position.set(radius * Math.cos(angle), 0, radius * Math.sin(angle));

    moonGroup.add(moon);
    moons.push(moon);
  }
  planet.position.set(x, 0, z); // Set the position on the circle

  scene.add(planet);
  planets.push(planet);

  // Create and add the label to the planet
  const label = createLabel(bigPlanetIds[i]);
  planet.add(label);
}

// Add orbit controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Add a light source to enable shadows
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(10, 10, 10);
light.castShadow = true;
scene.add(light);

// Enable shadows for the renderer
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const jewelTexture2 = textureLoader.load("https://media.istockphoto.com/id/1262751373/photo/shiny-mint-green-glitter-texture-background.jpg?s=612x612&w=0&k=20&c=x05vGtuagMoD7ZIaTIz3-4n4GYNAccN33wKRC4wtS6k=");
const bigPlanetMaterial2 = new THREE.MeshStandardMaterial({
  map: jewelTexture2,
});

// Set up shadows for the planets
planets.forEach((planet) => {
    planet.receiveShadow = true;
    planet.castShadow = true;
    if (planet == newPlanet) {
      planet.material = bigPlanetMaterial2;
    }
});

// Animate the zooming effect
function animateZoom() {
  const initialZoom = 2000; // Desired initial zoom level (more zoomed out)
  const targetZoom = 15; // Desired zoom level at the end
  const initialZoomSpeed = 29; // Initial zoom speed
  const finalZoomSpeed = 29; // Zoom speed when approaching the target
  // Interpolate between the initial and final zoom speed based on the distance to the targey
  const zoomSpeed = THREE.MathUtils.lerp(finalZoomSpeed, initialZoomSpeed, (camera.position.z - targetZoom) / (initialZoom - targetZoom));
  if (camera.position.z > targetZoom) {
    camera.position.z -= zoomSpeed;
    camera.position.y -= zoomSpeed * 0.08; // Adjust this value to control the vertical position of the camera during zoom-in
    camera.rotation.x = THREE.MathUtils.lerp(camera.rotation.x, -Math.PI / 6, 0.05); // Adjust this value to control the camera angle
  } else {
    camera.position.z = targetZoom;
  }
  camera.lookAt(scene.position);
  renderer.render(scene, camera); // Render the scene after updating the camera position
  // Continue the zoom animation if not yet at the target zoom
  if (camera.position.z != targetZoom) {
    requestAnimationFrame(animateZoom);
  } else {
    // Once zooming is complete, start the regular animation
    animate();
  }
}
// function animateZoom() {
//   const targetZoom = 12; // Desired zoom level
//   const zoomSpeed = 8; // Speed of zooming

//   if (camera.position.z > targetZoom) {
//     camera.position.z -= zoomSpeed;
//     camera.lookAt(scene.position);
//     renderer.render(scene, camera); // Render the scene after updating the camera position
//     requestAnimationFrame(animateZoom);
//     animate();
//   }
// }

function createStarTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 64;
  canvas.height = 64;

  const context = canvas.getContext('2d');
  const gradient = context.createRadialGradient(32, 32, 0, 32, 32, 32);

  gradient.addColorStop(0.0, 'rgba(255, 255, 255, 1)');
  gradient.addColorStop(0.2, 'rgba(255, 255, 255, 0.5)');
  gradient.addColorStop(1.0, 'rgba(255, 255, 255, 0)');

  context.fillStyle = gradient;
  context.fillRect(0, 0, 64, 64);

  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}

function createShootingStar() {
  const shootingStarGeometry = new THREE.TorusKnotGeometry(1, 0.4, 66, 14, 7, 20);
  const starTexture = createStarTexture();
  const shootingStarMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00, map: starTexture });

  return new THREE.Mesh(shootingStarGeometry, shootingStarMaterial);
}

const shootingStars = [];

for (let i = 0; i < 100; i++) { // Create 100 shooting stars
  const shootingStar = createShootingStar();
  shootingStar.position.set(
    Math.random() * 2000 - 1000,
    Math.random() * 2000 - 1000,
    Math.random() * 2000 - 1000
  );
  shootingStar.userData.direction = new THREE.Vector3(
    Math.random() - 0.5,
    Math.random() - 0.5,
    Math.random() - 0.5
  );
  shootingStars.push(shootingStar);
  scene.add(shootingStar);
}

// // Load the horizon texture
// const horizonTextureURL  = 'https://images.unsplash.com/photo-1465101162946-4377e57745c3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1778&q=80';

// // Load the horizon texture
// const horizonTexture = new THREE.TextureLoader().load(horizonTextureURL);

// // Create the sphere geometry
// const horizonGeometry = new THREE.SphereGeometry(600, 32, 32); // Adjust the radius to fit your scene

// // Create the material using the texture
// const horizonMaterial = new THREE.MeshBasicMaterial({
//   map: horizonTexture,
//   side: THREE.BackSide // This makes the texture visible from inside the sphere
// });

// // Create the mesh and add it to the scene
// const horizonSphere = new THREE.Mesh(horizonGeometry, horizonMaterial);
// scene.add(horizonSphere);

let hoveredPlanet = null;
// Render the scene

function animate() {
  requestAnimationFrame(animate);

  // Move the shooting stars
  shootingStars.forEach((star) => {
    star.position.add(star.userData.direction);

    // Reset the position if the star goes out of bounds
    if (Math.abs(star.position.x) > 1000 ||
        Math.abs(star.position.y) > 1000 ||
        Math.abs(star.position.z) > 1000) {
      star.position.set(
        Math.random() * 2000 - 1000,
        Math.random() * 2000 - 1000,
        Math.random() * 2000 - 1000
      );
    }
  });

  planets.forEach((planet, index) => {
    // Check if this planet is the currently hovered one
    const isHovered = planet === hoveredPlanet;

    // If it's hovered, don't rotate; otherwise, rotate it
    if (!isHovered) {
      planet.rotation.y += 0.003;
    }

    const moonGroup = moons.slice(index * 6, (index + 1) * 6);
    moonGroup.forEach((moon, moonIndex) => {
      const angle = moonIndex * ((2 * Math.PI) / 6);
      const radius = 2;

      // Set the position based on the radius and angle
      moon.position.set(radius * Math.cos(angle), 0, radius * Math.sin(angle));
    });

    const label = planet.children.find((child) => child.type === "Sprite");
    label.position.set(0, 1.5, 0);
  });

  // Update the position of the new planet's label
  const newLabel = newPlanet.children.find((child) => child.type === "Sprite");
  newLabel.position.set(0, 1.5, 0);

  // Rotate the horizon sphere
  // horizonSphere.rotation.y += 0.0001;

  controls.update();
  renderer.render(scene, camera);
}

function sendClickData(clickData) {
  const clickDataJSON = JSON.stringify(clickData);

  let url = "/update_data";
  let redirectUrl = "/dashboard";

  if (clickData.categorical_variable === "POS_entrymode") {
    url = "/update_data";
    redirectUrl = "/pos";
  }

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: clickDataJSON,
  })
    .then((response) => {
      if (response.ok) {
        window.location.href = redirectUrl;
      } else {
        throw new Error("POST request failed");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Create a container element for the tooltip
const tooltipContainer = document.createElement("div");
tooltipContainer.style.position = "absolute";
tooltipContainer.style.pointerEvents = "none"; // To not interfere with raycasting
tooltipContainer.style.padding = "10px";
tooltipContainer.style.display = "none"; // Hide by default
tooltipContainer.style.color = "white";
tooltipContainer.style.textShadow = "2px 2px 4px rgba(0, 0, 0, 0.5)";
tooltipContainer.style.fontFamily = "'FF Tisa Sans', sans-serif";
document.body.appendChild(tooltipContainer);

function onMouseMove(event) {
  // Calculate normalized device coordinates
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  // Raycast from the camera through the mouse coordinates
  raycaster.setFromCamera(mouse, camera);

  // Perform intersection check with small planets
  const smallPlanetIntersects = raycaster.intersectObjects(moons, true);

  if (smallPlanetIntersects.length > 0) {
    const hoveredObject = smallPlanetIntersects[0].object;
    const bigPlanetId = hoveredObject.parent.parent.userData.bigPlanetId;
    const smallPlanetId = hoveredObject.userData.id;

    tooltipContainer.innerHTML = `Numerical Feature: ${smallPlanetId}<br>Belongs to Category: ${bigPlanetId}`;
    tooltipContainer.style.display = "block";
    tooltipContainer.style.left = `${event.clientX}px`;
    tooltipContainer.style.top = `${event.clientY}px`;

    // Set the currently hovered planet-moon system (the parent planet's parent group)
    hoveredPlanet = hoveredObject.parent.parent;

    return;
  }

  // Perform intersection check with big planets
  const bigPlanetIntersects = raycaster.intersectObjects(planets, true);

  if (bigPlanetIntersects.length > 0) {
    const hoveredObject = bigPlanetIntersects[0].object;
    const bigPlanetId = hoveredObject.userData.bigPlanetId;

    tooltipContainer.innerHTML = `Category: ${bigPlanetId}`;
    tooltipContainer.style.display = "block";
    tooltipContainer.style.left = `${event.clientX}px`;
    tooltipContainer.style.top = `${event.clientY}px`;

    // Set the currently hovered planet
    hoveredPlanet = hoveredObject;

    return;
  }

  // If no intersections, reset the currently hovered planet
  hoveredPlanet = null;

  // Hide the tooltip if there are no intersections
  tooltipContainer.style.display = "none";
}
// Attach mouse move event listener to the document
document.addEventListener("mousemove", onMouseMove, false);

animateZoom();