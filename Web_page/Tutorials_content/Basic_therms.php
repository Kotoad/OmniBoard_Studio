<!DOCTYPE html>
<html lang="en">

<?php $page_title = "Basic Electronics & Circuit Diagrams"; include '../Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            Basic Electronics & Circuit Diagrams
        </h1>
        <p class="text-lg text-slate-400 mb-10 max-w-2xl mx-auto">
            Understand essential electrical quantities, symbols, and wiring principles before building projects.
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6">Electrical and Magnetic Quantities</h2>
            <p class="text-slate-300 mb-4">Before diving into building circuits, it's important to understand some
                fundamental electrical and magnetic quantities that are commonly used in electronics. These quantities
                help us describe and analyze the behavior of electrical circuits and components.</p>
            <p class="text-slate-300 mb-4">Here are some of the key electrical and magnetic quantities you should be
                familiar with:</p>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span>Electric Quantities:</span>
                    <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Electric charge</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span> A fundamental property of matter that causes it to experience a force when placed in
                                an electric field, measured in coulombs (C) and represented by "Q".
                                In simple terms, it can be thought of as the "quantity" of electricity, where a higher
                                charge indicates more electric particles present.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Electric voltage</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>In electrical terms is a potential difference between two points in a circuit,
                                measured in volts (V) and it's represented by the symbol "V" in American English and "U"
                                in European English.
                                In simple terms, it can be thought of as the "pressure" that pushes electric charges
                                through a conductor, enabling the flow of current.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Electric current</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The flow of electric charge through a conductor, measured in amperes (A) and
                                represented by "I".
                                It represents the rate at which electric charges pass through a point in a circuit.
                                There are two types of electric current: direct current (DC), where the flow of charge
                                is in one direction, and alternating current (AC), where the flow of charge periodically
                                reverses direction.
                                In simple terms, it can be thought of as the "flow" of electricity, where a higher
                                current indicates a greater flow of electric charge.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Electric resistance</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The opposition to the flow of electric current, measured in ohms (Ω) and represented
                                by "R".
                                It determines how much current will flow for a given voltage, the rest will turn to
                                heat.
                                In simple terms, it can be thought of as the "friction" that impedes the flow of
                                electricity, where a higher resistance results in less current flow for a given
                                voltage.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Electric power</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The rate at which electrical energy is transferred or consumed, measured in watts (W)
                                and represented by "P".
                                In simple terms, it can be thought of as the "work" done by electricity, where a higher
                                power indicates more energy being transferred or consumed.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Electric conductance</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The reciprocal of resistance, measured in siemens (S) and represented by "G".
                                In simple terms, it can be thought of as the "ease" with which electricity flows through
                                a conductor, where a higher conductance indicates less resistance and easier flow of
                                electric current.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Electric energy</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The capacity to do work, measured in joules (J) and represented by "E".
                                In simple terms, it can be thought of as the "fuel" that powers electrical devices,
                                where a higher energy indicates more capacity to perform work.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Electric capacity</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The ability of a system to store electric charge, measured in farads (F) and
                                represented by "C".
                                In simple terms, it can be thought of as the "storage" for electricity, where a higher
                                capacity indicates a greater ability to store electric charge.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Electric inductance</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The property of a conductor that opposes changes in current, measured in henries (H)
                                and represented by "L".
                                In simple terms, it can be thought of as the "inertia" of electricity, where a higher
                                inductance indicates a greater opposition to changes in current flow.</span>
                        </li>
                    </ul>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span>Magnetic Quantities:</span>
                    <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Magnetic flux</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The total magnetic field passing through a given area, measured in webers (Wb) and
                                represented by "Φ".
                                In simple terms, it can be thought of as the "amount" of magnetism, where a higher
                                magnetic flux indicates a stronger magnetic field passing through an area.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Magnetic field strength</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The intensity of a magnetic field, measured in teslas (T) and represented by "B".
                                In simple terms, it can be thought of as the "strength" of magnetism, where a higher
                                magnetic field strength indicates a stronger magnetic field.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Magnetic permeability</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The ability of a material to support the formation of a magnetic field, measured in
                                henries per meter (H/m) and represented by "μ".
                                In simple terms, it can be thought of as the "friendliness" of a material to magnetism,
                                where a higher magnetic permeability indicates that the material allows magnetic fields
                                to pass through it more easily.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Magnetic reluctance</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The opposition to the creation of a magnetic field in a material, measured in
                                ampere-turns per weber (At/Wb) and represented by "R_m".
                                In simple terms, it can be thought of as the "resistance" to magnetism, where a higher
                                magnetic reluctance indicates that the material opposes the formation of a magnetic
                                field more strongly.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Magnetic energy</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The energy stored in a magnetic field, measured in joules (J) and represented by
                                "E_m".
                                In simple terms, it can be thought of as the "potential" of magnetism, where a higher
                                magnetic energy indicates that more energy is stored in the magnetic field.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Magnetic force</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>The force exerted by a magnetic field on moving charges or other magnets, measured in
                                newtons (N) and represented by "F_m".
                                In simple terms, it can be thought of as the "push" or "pull" of magnetism, where a
                                higher magnetic force indicates a stronger interaction between the magnetic field and
                                charged particles or other magnets.</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">Magnetic moment</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span>A measure of the strength and orientation of a magnet's magnetic field, measured in
                                ampere-square meters (A·m²) and represented by "m".
                                In simple terms, it can be thought of as the "personality" of a magnet, where a higher
                                magnetic moment indicates a stronger and more oriented magnetic field.</span>
                        </li>
                    </ul>
                </li>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6">Common Electrical Terms and Symbols</h2>
            <p class="text-slate-300 mb-4">In addition to understanding the fundamental electrical and magnetic
                quantities, it's also important to familiarize yourself with common electrical terms and symbols that
                are used in circuit diagrams and electronics discussions. These terms and symbols help us communicate
                effectively about electronic components, circuits, and concepts.</p>
            <p class="text-slate-300 mb-4">Here are some common electrical terms and symbols you should know:</p>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">Ground</span>
                </li>
                <li class="flex items-start gap-3">
                    <span> A reference point in an electrical circuit from which voltages are measured, a common return
                        path for electric current.
                        In simple terms, it can be thought of as the "zero" point in a circuit, where all voltages are
                        measured relative to it and it provides a path for current to return to the source.
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Ground_Symbol.png" alt="Ground Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1">Ground Symbol</figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">Power Supply</span>
                </li>
                <li class="flex items-start gap-3">
                    <span> A source of electrical power for the circuit, providing the necessary voltage and current.
                        In simple terms, it can be thought of as the "heart" of a circuit, where it provides the energy
                        needed for the circuit to function.
                    </span>
                </li>
                <div class="w-full flex justify-center gap-12 mt-4">
                    <figure class="flex flex-col items-center">
                        <img src="Basic_therms/Power_Supply_Symbol_DC.png" alt="Power Supply Symbol DC"
                            class="max-w-full h-auto">
                        <figcaption class="text-xs text-slate-400 mt-1">Power Supply Symbol (DC)</figcaption>
                    </figure>
                    <figure class="flex flex-col items-center">
                        <img src="Basic_therms/Power_Supply_Symbol_AC.png" alt="Power Supply Symbol AC"
                            class="max-w-full h-auto">
                        <figcaption class="text-xs text-slate-400 mt-1">Power Supply Symbol (AC)</figcaption>
                    </figure>
                </div>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">Pin symbol</span>
                </li>
                <li class="flex items-start gap-3">
                    <span> A symbol representing a connection point on a your RPI by number</span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Pin_Connection_Symbol.png" alt="Pin Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1">Pin Symbol</figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">Resistor</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>A component that resists the flow of electric current, used to control voltage and current in
                        a circuit.
                        In simple terms, it can be thought of as the "brake" of a circuit, where it limits the flow of
                        electricity to protect other components and control the behavior of the circuit.
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Resistor_Symbol.png" alt="Resistor Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1">Resistor Symbol</figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">Capacitor</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>A component that stores and releases electrical energy, used for filtering, timing, and energy
                        storage in circuits.
                        In simple terms, it can be thought of as the "battery" of a circuit, where it temporarily stores
                        electrical energy and releases it when needed to smooth out voltage fluctuations or provide
                        power during brief interruptions.
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Capacitor_Symbol.png" alt="Capacitor Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1">Capacitor Symbol</figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">Inductor</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>A component that stores energy in a magnetic field when electric current flows through it,
                        used for filtering, energy storage, and inductive coupling in circuits.
                        In simple terms, it can be thought of as the "coil" of a circuit, where it creates a magnetic
                        field that can store energy and oppose changes in current flow, making it useful for filtering
                        and energy storage applications.
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Inductor_Symbol.png" alt="Inductor Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1">Inductor Symbol</figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">Diode</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>A component that allows current to flow in one direction only, used for rectification, signal
                        modulation, and protection in circuits.
                        In simple terms, it can be thought of as the "one-way valve" of a circuit, where it permits the
                        flow of electricity in one direction while blocking it in the opposite direction, making it
                        essential for controlling current flow and protecting components from reverse voltage.
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Diode_Symbol.png" alt="Diode Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1">Diode Symbol</figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">LED diode</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>
                        A type of diode that emits light when current flows through it, used for indication and display
                        purposes in circuits.
                        In simple terms, it can be thought of as the "light bulb" of a circuit, where it produces light
                        when electricity flows through it, making it useful for visual indicators and displays.
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/LED_Symbol.png" alt="LED Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1">LED Symbol</figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">Transistor</span>
                </li>
                <li class="flex items-start gap-3">
                    <span>A semiconductor device used to amplify or switch electronic signals, essential for building
                        complex circuits and digital logic.
                        In simple terms, it can be thought of as the "amplifier" or "switch" of a circuit, where it can
                        control the flow of electricity based on an input signal, making it fundamental for
                        amplification and digital logic applications.
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Transistor_Symbol.png" alt="Transistor Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1">Transistor Symbol</figcaption>
                </figure>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>
</body>

</html>