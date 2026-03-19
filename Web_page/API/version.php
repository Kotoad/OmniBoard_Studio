<?php
header('Content-Type: application/json');
echo json_encode([
    "tag_name" => "V0.1.0",
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