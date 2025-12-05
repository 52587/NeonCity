# Neon City - Procedural Cyberpunk City Generator

**Neon City** is a real-time procedural simulation written entirely in Python using PyOpenGL. The goal was to create an atmospheric cyberpunk skyline that feels organic and dense, avoiding the repetitive look of standard grid-based cities.

![Neon City Screenshot](https://github.com/52587/NeonCity/assets/placeholder.png)
*(Note: You can replace this link with an actual screenshot of your project)*

## Features
*   **Organic Layout:** Uses a **Rejection Sampling** algorithm with AABB collision detection to place buildings naturally, creating varied alleyways and non-grid layouts.
*   **Procedural Skyline:** Utilizes **Perlin Noise** to generate smooth height maps, creating distinct neighborhoods with realistic vertical flow.
*   **Dynamic Themes:** 5 distinct cyberpunk color palettes (Neon Cool, Neon Warm, Matrix, Vaporwave, Toxic) that update lighting, fog, and background in real-time.
*   **Optimized Rendering:** Implements **OpenGL Display Lists** for high-performance rendering (60 FPS) and **MSAA/Linear Fog** for visual fidelity.
*   **Interactive Camera:** Dynamic camera system that scales with the city size, featuring orbit controls and a pause function.

## How to Run

### Option 1: Standalone Executable (Windows)
1.  Go to the [Releases Page](https://github.com/52587/NeonCity/releases).
2.  Download `NeonCity.exe`.
3.  Run the file. No Python installation required.

### Option 2: From Source
1.  Install Python 3.10+.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the simulation:
    ```bash
    python main.py
    ```

## Controls
*   **Arrow Up/Down:** Increase/Decrease City Density (Map grows dynamically).
*   **Space:** Cycle Color Themes.
*   **P:** Pause/Unpause Camera Rotation.
*   **Mouse Click:** Launch Fireworks.
*   **ESC:** Quit.

---

## Project Postmortem

### What Worked Well
*   **Procedural Generation:** The transition from a rigid grid system to a **Rejection Sampling** algorithm was the most significant improvement. Combined with **Perlin Noise** for height distribution, it successfully transformed the city from a checkerboard pattern into an organic, believable skyline with distinct neighborhoods and alleyways.
*   **Performance Optimization:** Python is generally slow for real-time rendering, but implementing **OpenGL Display Lists** was a game-changer. By compiling geometry on the GPU and only regenerating it when necessary (e.g., during theme changes), we achieved a stable 60 FPS even at high densities.
*   **Atmosphere:** The combination of **Linear Fog**, **MSAA (Anti-Aliasing)**, and the **Polygon Offset** technique for windows solved the visual artifacts (jagged edges, Z-fighting) that plagued early builds. The dynamic theme system added significant visual variety without requiring new assets.

### What Didn't Work Out
*   **Immediate Mode OpenGL:** Relying on legacy OpenGL (`glBegin`/`glEnd`) made the project easy to prototype but difficult to port. Because modern web browsers (WebGL) do not support these commands, we could not easily deploy the simulation to the web, limiting accessibility.
*   **Collision Scalability:** The current collision detection is a naive O(N^2) check. While fine for 100-200 buildings, the generation time slows down noticeably at very high densities.
*   **Camera Logic:** Getting the camera to feel "right" was a struggle. Early versions were either too far away or clipped through buildings. It took several iterations of math to link the camera's orbit radius and height dynamically to the city's bounding box.

### What I Would Do Differently
*   **Modern OpenGL Pipeline:** If I were to start over, I would use **Vertex Buffer Objects (VBOs)** and **Shaders**. This would not only improve performance further but would also allow for advanced lighting effects (like bloom or real-time shadows) and make the project compatible with WebGL for browser deployment.
*   **Spatial Partitioning:** To support massive cities (1000+ buildings), I would implement a spatial partition system (like a Quadtree or a simple spatial hash grid) to speed up the collision detection during the generation phase.

---

## Artistic Statement

I created **Neon City** to explore the intersection of order and chaos in digital urban environments.

In many procedural city generators, the results often feel sterile—perfect grids of identical boxes that lack the "lived-in" quality of real cities. I wanted to capture the aesthetic of **Cyberpunk**, a genre defined by its clutter, density, and overwhelming verticality.

By using algorithms that embrace randomness within constraints (Rejection Sampling) and smooth transitions (Perlin Noise), I aimed to create a skyline that feels grown rather than built. The project is designed not as a game, but as a digital mood piece—a window into an infinite, neon-soaked metropolis that invites the viewer to pause and watch the lights flicker in the distance.

---

## Credits

**Core Technologies:**
*   **Language:** Python 3.13
*   **Graphics Engine:** PyOpenGL (OpenGL 1.1 - 1.3)
*   **Windowing & Input:** PyGame CE

**Libraries:**
*   `noise`: Used for Perlin noise generation (height maps).
*   `pygame`: Used for window management, event loop, and font rendering.
*   `PyOpenGL`: Used for low-level graphics rendering.

**Assets:**
*   **Fonts:** Arial (Standard System Font).
*   **Art/Models:** All 3D geometry (buildings, particles) was generated procedurally via code. No external 3D models were used.

**Third-Party Tools:**
*   **PyInstaller:** Used to compile the standalone executable.
