<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniBoard Studio - Visual Programming Environment</title>
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
        <h1 class="text-5xl font-extrabold tracking-tight text-white mb-6">
            Visual Programming for Microcontrollers
        </h1>
        <p class="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
            Build and compile MicroPython projects seamlessly. A complete visual node environment with built-in code editing for Raspberry Pi Pico and more.
        </p>
        <div class="flex justify-center gap-4">
            <a href="/Download.php" class="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold text-lg hover:bg-blue-500 shadow-sm transition-all">
                Get Started
            </a>
            <a href="/Tutorials.php" class="bg-slate-800 border border-slate-700 text-slate-200 px-8 py-3 rounded-lg font-semibold text-lg hover:bg-slate-700 transition-all">
                Read Documentation
            </a>
        </div>
    </header>

    <main class="w-full py-20 flex-grow">
        <section id="features" class="bg-slate-900 py-20 border-t border-slate-800">
            <div class="max-w-5xl mx-auto px-6">
                <h2 class="text-3xl font-bold mb-12 text-center text-white">Core Features</h2>
                <div class="grid md:grid-cols-3 gap-8">
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400">Visual Node Editor</h3>
                        <p class="text-slate-400">Drag and drop logic blocks, timers, and hardware interfaces to build complex logic without writing syntax manually.</p>
                    </div>
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400">Integrated Compiler</h3>
                        <p class="text-slate-400">Instantly translate visual node graphs into optimized MicroPython code ready for deployment to connected devices.</p>
                    </div>
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400">Hardware Support</h3>
                        <p class="text-slate-400">Native support and setup workflows for the Raspberry Pi Pico series and Raspberry Pi 1 to 5.</p>
                    </div>
                </div>
                <h2 class="text-3xl font-bold mt-20 mb-12 text-center text-white">Future Developments</h2>
                <div class="grid md:grid-cols-3 gap-8">
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400">Expanded Hardware Support</h3>
                        <p class="text-slate-400">Adding compatibility with more microcontroller platforms and single-board computers beyond the Raspberry Pi ecosystem.</p>
                    </div>
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400">Advanced Node Types</h3>
                        <p class="text-slate-400">Introducing new node categories for more complex logic, data processing, and hardware interactions.</p>
                    </div>
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400">Community Contributions</h3>
                        <p class="text-slate-400">Encouraging users to share their own node templates, tutorials, and project ideas to foster a collaborative learning environment.</p>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <?php include 'Footer.php'; ?>

</body>
</html>