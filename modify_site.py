import re

with open('/home/alpha/shadowdev_portfolio/index.html', 'r') as f:
    html = f.read()

# 1. Replace Colors
html = html.replace("neonBlue: '#00f3ff'", "mint: '#00ffa6'")
html = html.replace("neonPurple: '#9d00ff'", "deepViolet: '#5b00ff'")
html = html.replace('neonBlue', 'mint')
html = html.replace('neonPurple', 'deepViolet')
html = html.replace('amber-500', 'mint')

# 2. Fix the Hero Canvas Class
html = html.replace('<canvas id="hero-canvas" class="absolute inset-0 w-full h-full z-0 pointer-events-none"></canvas>',
                    '<canvas id="hero-canvas" class="fixed inset-0 w-full h-full z-[-1] pointer-events-none"></canvas>')

# 3. Update the SHADOWDEV Text styles
old_style = """                    text-shadow: 
                        0 0 10px rgba(255, 115, 0, 0.5),
                        0 0 40px rgba(255, 170, 0, 0.8),
                        0 0 80px rgba(255, 200, 0, 1),
                        0 0 120px rgba(255, 115, 0, 0.8),
                        inset 0 0 20px rgba(0, 0, 0, 1);
                    -webkit-text-stroke: 1px rgba(255, 170, 0, 0.3);"""

new_style = """                    text-shadow: 
                        0 0 10px rgba(0, 255, 166, 0.5),
                        0 0 40px rgba(91, 0, 255, 0.8),
                        0 0 80px rgba(0, 255, 166, 1),
                        0 0 120px rgba(91, 0, 255, 0.8),
                        inset 0 0 20px rgba(0, 0, 0, 1);
                    -webkit-text-stroke: 1px rgba(0, 255, 166, 0.3);"""

html = html.replace(old_style, new_style)

# 4. Remove old Three.js logic entirely and replace with new Morphing logic
script_start = html.find('<!-- Three.js Anti-Gravity Particles Logic -->')
if script_start != -1:
    html = html[:script_start]

new_js = """
    <!-- Three.js Morphing Living Interface Logic -->
    <script>
        const canvas = document.getElementById('hero-canvas');
        if (canvas) {
            const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
            camera.position.z = 30;

            const count = 15000;
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(count * 3);
            const colors = new Float32Array(count * 3);
            
            // Generate targets
            const orbPts = [];
            const galPts = [];
            const braPts = [];
            const currentPts = [];

            const colorMint = new THREE.Color(0x00ffa6);
            const colorViolet = new THREE.Color(0x5b00ff);

            for (let i = 0; i < count; i++) {
                // Orb
                const uOrb = Math.random() * Math.PI;
                const vOrb = Math.random() * 2 * Math.PI;
                const rOrb = 12 + Math.random() * 2;
                orbPts.push(new THREE.Vector3(
                    rOrb * Math.sin(uOrb) * Math.cos(vOrb),
                    rOrb * Math.sin(uOrb) * Math.sin(vOrb),
                    rOrb * Math.cos(uOrb)
                ));

                // Galaxy
                const angle = Math.random() * Math.PI * 2;
                const radius = Math.random() * 40;
                const spiralAngle = angle + (radius * 0.2);
                galPts.push(new THREE.Vector3(
                    Math.cos(spiralAngle) * radius,
                    (Math.random() - 0.5) * (40 - radius) * 0.1,
                    Math.sin(spiralAngle) * radius - 15 // tilt back
                ));

                // Brain
                const hemisphere = Math.random() > 0.5 ? 1 : -1;
                const uBra = Math.random() * Math.PI;
                const vBra = Math.random() * 2 * Math.PI;
                let rBra = 15;
                rBra += Math.sin(uBra * 8) * Math.cos(vBra * 8) * 1.5; // folds
                braPts.push(new THREE.Vector3(
                    (rBra * Math.sin(uBra) * Math.cos(vBra)) + (hemisphere * 8),
                    (rBra * 0.8) * Math.sin(uBra) * Math.sin(vBra) + 5,
                    (rBra * 1.2) * Math.cos(uBra)
                ));

                currentPts.push(orbPts[i].clone());
                
                // Initial colors
                colors[i * 3] = colorMint.r;
                colors[i * 3 + 1] = colorMint.g;
                colors[i * 3 + 2] = colorMint.b;
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            // Custom shader for glowing points
            const material = new THREE.PointsMaterial({
                size: 0.15,
                vertexColors: true,
                transparent: true,
                opacity: 0.8,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            });

            const pointCloud = new THREE.Points(geometry, material);
            scene.add(pointCloud);

            // Mouse tracking
            let mouse = new THREE.Vector2(-999, -999);
            window.addEventListener('mousemove', (e) => {
                mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            });

            const raycaster = new THREE.Raycaster();
            const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
            const intersectPoint = new THREE.Vector3();

            const clock = new THREE.Clock();

            function animate() {
                requestAnimationFrame(animate);
                const time = clock.getElapsedTime();

                raycaster.setFromCamera(mouse, camera);
                raycaster.ray.intersectPlane(plane, intersectPoint);

                let scrollY = window.scrollY;
                let maxScroll = document.body.scrollHeight - window.innerHeight;
                let progress = Math.min(1, Math.max(0, scrollY / (maxScroll || 1)));

                let t1 = Math.min(1, progress * 2);
                let t2 = Math.max(0, (progress - 0.5) * 2);
                
                // Slowly rotate whole cloud
                pointCloud.rotation.y = time * 0.1;

                const posAttr = geometry.attributes.position.array;
                const colAttr = geometry.attributes.color.array;

                for (let i = 0; i < count; i++) {
                    let target = new THREE.Vector3();
                    if (progress < 0.5) {
                        target.lerpVectors(orbPts[i], galPts[i], t1);
                    } else {
                        target.lerpVectors(galPts[i], braPts[i], t2);
                    }

                    // Breathing effect
                    let breath = Math.sin(time * 2 + (i % 10)) * 0.5;
                    target.x += breath * (target.x / 20);
                    target.y += breath * (target.y / 20);
                    target.z += breath * (target.z / 20);

                    // Inverse transform mouse point to local space for interaction
                    let localIntersect = intersectPoint.clone();
                    pointCloud.worldToLocal(localIntersect);

                    // Mouse interaction
                    let dist = localIntersect.distanceTo(target);
                    if (dist < 8) {
                        let force = (8 - dist) / 8;
                        target.x += (target.x - localIntersect.x) * force * 1.5;
                        target.y += (target.y - localIntersect.y) * force * 1.5;
                    }

                    currentPts[i].lerp(target, 0.05);

                    posAttr[i * 3] = currentPts[i].x;
                    posAttr[i * 3 + 1] = currentPts[i].y;
                    posAttr[i * 3 + 2] = currentPts[i].z;

                    // Color mix based on position/progress
                    let mixFactor = progress + (Math.sin(time + i) * 0.2);
                    let c = colorMint.clone().lerp(colorViolet, mixFactor);
                    colAttr[i * 3] = c.r;
                    colAttr[i * 3 + 1] = c.g;
                    colAttr[i * 3 + 2] = c.b;
                }

                geometry.attributes.position.needsUpdate = true;
                geometry.attributes.color.needsUpdate = true;

                renderer.render(scene, camera);
            }

            animate();

            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
        }
    </script>
</body>
</html>
"""

html += new_js

with open('/home/alpha/shadowdev_portfolio/index.html', 'w') as f:
    f.write(html)
print("index.html successfully updated")
