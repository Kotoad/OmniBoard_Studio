<?php
header('Content-Type: application/json');
echo json_encode([
    "tag_name" => "v0.22.3",
    "assets" => [   
        [
            "name" => "OmniBoard_Online_Installer.exe",
            "download_url" => "https://omniboardstudio.cz/downloads/OmniBoard_Online_Installer.exe"
        ],
        [
            "name" => "OmniBoard_Studio_Linux.tar.gz",
            "download_url" => "https://omniboardstudio.cz/downloads/OmniBoard_Studio_Linux.tar.gz"
        ]
    ]
]);