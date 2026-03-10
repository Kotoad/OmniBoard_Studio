<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniBoard Studio - Download</title>
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
        <h1 class="text-4xl font-bold mb-6 text-white">Download OmniBoard Studio</h1>
        <p class="text-slate-400 text-xl mb-10 max-w-2xl mx-auto">Get the latest version of OmniBoard Studio for your platform. Follow the instructions below to install and start building your projects.</p>
    </header>

    <main class="w-full py-20 flex-grow">
        <section id="download" class="bg-slate-900 py-20 border-t border-slate-800">
            <div class="max-w-5xl mx-auto px-6">
                <h2 class="text-3xl font-bold mb-12 text-center text-white">Available Downloads</h2>
                <div class="grid md:grid-cols-2 gap-8">
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800 text-center">
                        <h2 class="text-2xl font-semibold mb-4 text-blue-400">Windows</h2>
                        <p class="text-slate-400 mb-6">Download the Windows installer to get started quickly.</p>
                        <a href="https://github.com/Kotoad/APP_PyQt/releases/latest/download/OmniBoard_Online_Installer.exe" download class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition-colors">Download for Windows</a>
                    </div>
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800 text-center">
                        <h2 class="text-2xl font-semibold mb-4 text-blue-400">Linux</h2>
                        <p class="text-slate-400 mb-6">Get the Linux version of OmniBoard Studio for your GNU/Linux systems.</p>
                        <a href="https://github.com/Kotoad/APP_PyQt/releases/latest/download/install.sh" download class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition-colors">Download for Linux</a>
                    </div>
                </div>
                <div class="mt-20 text-center">
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400">Other Platforms</h2>
                    <p class="text-slate-400 mb-6">We are actively working on expanding support to other platforms. Stay tuned for updates!</p>
                </div>
            </div>
        </section>
    </main>

    <?php include 'Footer.php'; ?>

</body>
</html>