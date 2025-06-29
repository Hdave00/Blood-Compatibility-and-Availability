// blood cell visualuzation using Three.js, mostly copied from the documentation samples to create a basic model to visually represent a blood cell
// a lot of help was given by the ddb/cs50.ai

import * as THREE from 'three'; // the only import needed as the docs mention it https://threejs.org/manual/#en/installation

// BloodCell3D.js - Three.js blood cell model ie, the model itself

// Lighting strength (directionalLight.intensity = 1.5;)

// Antigen distance (x = Math.cos(angle) * 1.4;)

// Roughness/Metalness in materials.

// this class is basically the object that will be called in the DOM/html file and we wrap all its function inside this class.
// we immediately make a constructor with arguments being the container element ie, the box that will show the animation and the different blood types.
// then come the functions that basically say, what do we want this construction too look like, so we add a bloodcell, a lighting objects and antigens and we add the antigens
// then the last function within the whole class is the animate function which will make it spin.
class BloodCell3D {
    constructor(containerElement, bloodType) {
      this.container = containerElement;
      this.bloodType = bloodType;
      this.scene = new THREE.Scene();
      this.scene.background = new THREE.Color(0x222222);
      this.camera = new THREE.PerspectiveCamera(75, this.container.clientWidth / this.container.clientHeight, 0.1, 1000);
      this.renderer = new THREE.WebGLRenderer({ antialias: true });
      this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
      this.container.appendChild(this.renderer.domElement);
      console.log("Renderer DOM element added to container");

      this.createLighting();
      this.createBloodCell();
      this.addAntigens();

      // camera’s position is set to predetermined coordinates which should be fine for viewing the scene.
      this.camera.position.set(0, 0, 3);
      this.animate();
      console.log(this.camera.position);
    }

    createLighting() {
        // add ambient light to brighten everything
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        // add a stronger directional light to highlight the blood cell
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);

        console.log("Lights added to scene");
    }

    createBloodCell() {
        const geometry = new THREE.SphereGeometry(1, 32, 32);
        const material = new THREE.MeshStandardMaterial({
            color: 0xff0000,  // ensure its bright red
            metalness: 0.2,   // add some reflectiveness
            roughness: 0.5    // not too shiny
        });

        this.bloodCell = new THREE.Mesh(geometry, material);
        this.scene.add(this.bloodCell);
        console.log("Blood cell mesh added to scene");
    }

    addAntigens() {
      if (this.bloodType === 'A' || this.bloodType === 'AB') {
        this.addAntigenGroup(0xff00ff, 10); // pink antigens
      }
      if (this.bloodType === 'B' || this.bloodType === 'AB') {
        this.addAntigenGroup(0x00aaaa, 10); // blue-green antigens
      }
    }

    addAntigenGroup(color, count) {
        const antigenMaterial = new THREE.MeshStandardMaterial({
            color,
            metalness: 0.3,
            roughness: 0.7
        });

        for (let i = 0; i < count; i++) {
            const antigen = new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 16), antigenMaterial);

            // spread them around the blood cell surface (copied from other models in the sample docs in Three.js and a lot of help from the CS50 ai)
            const angle = (i / count) * Math.PI * 2;
            const x = Math.cos(angle) * 1.3;
            const y = Math.sin(angle) * 1.3;
            const z = (Math.random() - 0.5) * 0.5;  // randomize depth

            antigen.position.set(x, y, z);
            this.bloodCell.add(antigen); // attach antigens to the blood cell
        }
    }

    animate() {
      requestAnimationFrame(() => this.animate());
      this.bloodCell.rotation.y += 0.01;
      this.renderer.render(this.scene, this.camera);
    }
  }

  // this line is important as it is used in the html file with react to call this class as an object when the blood cell visualiser is clicked,
  // to render it the correct way and in the right place.
  window.BloodCell3D = BloodCell3D;
