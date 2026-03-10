<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniBoard Studio - Tutorials</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group identify setPersonProperties setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags resetGroups onFeatureFlags addFeatureFlagsHandler onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
        posthog.init('phc_Mluykd4ZFp3kGqZaKOW5ZVppq7uvZhNzrGf2h9ZaRrQ', {
            api_host: 'https://eu.i.posthog.com',
            defaults: '2026-01-30'
        })
    </script>
</head>
<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include 'Navbar.php'; ?>

    <header class="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 class="text-4xl font-bold mb-6 text-white">OmniBoard Studio Tutorials</h1>
        <p class="text-slate-400 text-xl mb-10 max-w-2xl mx-auto">Explore our comprehensive tutorials to get the most out of OmniBoard Studio. Whether you're a beginner or an experienced maker, we have guides to help you build amazing projects.</p>
    </header>

    <div class="max-w-7xl mx-auto px-6 py-12 flex flex-col md:flex-row gap-10 flex-grow">

        <aside class="w-full md:w-64 shrink-0 hidden md:block">
            <nav class="sticky top-24 flex flex-col space-y-3 border-l-2 border-slate-800 pl-5">
                <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider mb-2">Getting Started</h3>
                <a href="/Tutorial_0_linux_based_RPI_variant_en.php" class="text-sm text-slate-400 hover:text-blue-400 transition-colors">Raspberry Pi Setup</a>
                <a href="/Tutorial_0_RPI_PICO_variant_en.php" class="text-sm text-slate-400 hover:text-blue-400 transition-colors">Raspberry Pi Pico Setup</a>
                
                <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider mb-2 mt-6">Core Concepts</h3>
                <a href="/Tutorials/Basic_therms.php" class="text-sm text-slate-400 hover:text-blue-400 transition-colors">Basic Electronic Principles</a>
                <a href="/Tutorials/Tutorial_2_en.php" class="text-sm text-slate-400 hover:text-blue-400 transition-colors">Understanding Nodes</a>
                <a href="/Tutorials/Tutorial_3_en.php" class="text-sm text-slate-400 hover:text-blue-400 transition-colors">Compiling Code</a>
                
                <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider mb-2 mt-6">Advanced</h3>
                <a href="/Tutorials/Tutorial_4_en.php" class="text-sm text-slate-400 hover:text-blue-400 transition-colors">Custom Blocks</a>
                <a href="/Tutorials/Tutorial_5_en.php" class="text-sm text-slate-400 hover:text-blue-400 transition-colors">Hardware Interfacing</a>
            </nav>
        </aside>

        <main class="flex-1">
            <section id="tutorials" class="bg-slate-900 py-20 border-t border-slate-800">
                <h2 class="text-3xl font-bold mb-12 text-white">Available Tutorials</h2>
                <div class="grid md:grid-cols-2 gap-6">
                    <a href="/Tutorials/Tutorial_0_linux_based_RPI_variant_en.php" class="block p-6 bg-slate-800 border border-slate-700 rounded-xl shadow-sm hover:border-blue-500 transition-all group">
                        <div class="text-sm font-semibold text-blue-400 mb-2 uppercase tracking-wide">Tutorial 0</div>
                        <h3 class="text-2xl font-bold mb-2 text-white group-hover:text-blue-400 transition-colors">Linux-based Raspberry Pi Setup</h3>
                        <p class="text-slate-400">Learn how to set up a Linux-based Raspberry Pi for use with OmniBoard Studio.</p>
                    </a>
                    
                    <a href="/Tutorials/Tutorial_0_RPI_PICO_variant_en.php" class="block p-6 bg-slate-800 border border-slate-700 rounded-xl shadow-sm hover:border-blue-500 transition-all group">
                        <div class="text-sm font-semibold text-blue-400 mb-2 uppercase tracking-wide">Tutorial 0</div>
                        <h3 class="text-2xl font-bold mb-2 text-white group-hover:text-blue-400 transition-colors">Raspberry Pi Pico Setup</h3>
                        <p class="text-slate-400">Learn how to flash the latest MicroPython firmware and prepare your board for OmniBoard Studio.</p>
                    </a>

                    <a href="/Tutorials/Basic_therms.php" class="block p-6 bg-slate-800 border border-slate-700 rounded-xl shadow-sm hover:border-blue-500 transition-all group">
                        <div class="text-sm font-semibold text-blue-400 mb-2 uppercase tracking-wide">Tutorial 1</div>
                        <h3 class="text-2xl font-bold mb-2 text-white group-hover:text-blue-400 transition-colors">Basic Electronic Principles</h3>
                        <p class="text-slate-400">Understand essential electrical quantities, symbols, and wiring principles before building projects.</p>
                    </a>

                    <a href="/Tutorials/Tutorial_2_en.php" class="block p-6 bg-slate-800 border border-slate-700 rounded-xl shadow-sm hover:border-blue-500 transition-all group">
                        <div class="text-sm font-semibold text-blue-400 mb-2 uppercase tracking-wide">Tutorial 2</div>
                        <h3 class="text-2xl font-bold mb-2 text-white group-hover:text-blue-400 transition-colors">First Project</h3>
                        <p class="text-slate-400">Build your first interactive project using OmniBoard Studio nodes.</p>
                    </a>
                </div>
            </section>
        </main>

    </div>

    <?php include 'Footer.php'; ?>

</body>
</html>