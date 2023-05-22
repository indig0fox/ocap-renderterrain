if (isNil "CBA_fnc_encodeJSON") then {
    CBA_fnc_encodeJSON = {

    // Function: CBA_fnc_encodeJSON

    // Description:
    // 	Serializes input to a JSON string. Can handle
    // 	- ARRAY
    // 	- BOOL
    // 	- CONTROL
    // 	- GROUP
    // 	- LOCATION
    // 	- NAMESPACE
    // 	- NIL (ANY)
    // 	- NUMBER
    // 	- OBJECT
    // 	- STRING
    // 	- TASK
    // 	- TEAM_MEMBER
    // 	- HASHMAP
    // 	- Everything else will simply be stringified.

    // Parameters:
    // 	_object - Object to serialize. <ARRAY, ...>

    // Returns:
    // 	_json   - JSON string containing serialized object.

    // Examples:
    // 	(begin example)
    // 		private _settings = call CBA_fnc_createNamespace;
    // 		_settings setVariable ["enabled", true];
    // 		private _json = [_settings] call CBA_fnc_encodeJSON;
    // 	(end)

    // Author:
    // 	BaerMitUmlaut

    params ["_object"];

    if (isNil "_object") exitWith { "null" };

    switch (typeName _object) do {
        case "SCALAR";
        case "BOOL": {
            str _object;
        };

        case "STRING": {
            {
                _object = [_object, _x#0, _x#1] call CBA_fnc_replace;
            } forEach [
                ["\", "\\"],
                ["""", "\"""],
                [toString [8], "\b"],
                [toString [12], "\f"],
                [endl, "\n"],
                [toString [10], "\n"],
                [toString [13], "\r"],
                [toString [9], "\t"]
            ];
            // Stringify without escaping inter string quote marks.
            """" + _object + """"
        };

        case "ARRAY": {
            if ([_object] call CBA_fnc_isHash) then {
                private _json = (([_object] call CBA_fnc_hashKeys) apply {
                    private _name = _x;
                    private _value = [_object, _name] call CBA_fnc_hashGet;

                    format ["%1: %2", [_name] call CBA_fnc_encodeJSON, [_value] call CBA_fnc_encodeJSON]
                }) joinString ", ";
                "{" + _json + "}"
            } else {
                private _json = (_object apply {[_x] call CBA_fnc_encodeJSON}) joinString ", ";
                "[" + _json + "]"
            };
        };

        case "HASHMAP": {
            private _json = ((_object toArray false) apply {
                _x params ["_key", ["_value", objNull]];

                if !(_key isEqualType "") then {
                    _key = str _key;
                };

                format ["%1: %2", [_key] call CBA_fnc_encodeJSON, [_value] call CBA_fnc_encodeJSON]
            }) joinString ", ";
            "{" + _json + "}"
        };

        default {
            if !(typeName _object in (supportInfo "u:allVariables*" apply {_x splitString " " select 1})) exitWith {
                [str _object] call CBA_fnc_encodeJSON
            };

            if (isNull _object) exitWith { "null" };

            private _json = ((allVariables _object) apply {
                private _name = _x;
                private _value = _object getVariable [_name, objNull];

                format ["%1: %2", [_name] call CBA_fnc_encodeJSON, [_value] call CBA_fnc_encodeJSON]
            }) joinString ", ";
            "{" + _json + "}"
        };
    };
};
};


[] spawn {
    if (!canSuspend) exitWith {
        "Must be spawned!"
    };

    OCAP_EXPORTER_ADDON = "ocap_exporter";
    OCAP_EXPORTER_VERSION = (OCAP_EXPORTER_ADDON callExtension "version");
    systemChat format["[%1]: Running extension version %2", OCAP_EXPORTER_ADDON, OCAP_EXPORTER_VERSION];

    OCAP_EXPORTER_SAVING = false;

    OCAP_EXPORTER_fnc_log = {
        params ["_message"];
        OCAP_EXPORTER_ADDON callExtension ["log", [_message]];
    };

    if (!isNil "OCAP_EXPORTER_CALLBACKHANDLE") then {
        removeMissionEventHandler ["ExtensionCallback", OCAP_EXPORTER_CALLBACKHANDLE];
        OCAP_EXPORTER_CALLBACKHANDLE = addMissionEventHandler ["ExtensionCallback", {
            params ["_name", "_function", "_data"];
            if !(_name == OCAP_EXPORTER_ADDON) exitWith {};
            // diag_log text format["[%1]: (%2) %3", OCAP_EXPORTER_ADDON, _function, _data];
            if (_function isEqualTo "finishWriting") exitWith {
                if (_data isEqualTo "SAVE STARTED") exitWith {
                    OCAP_EXPORTER_SAVING = true;
                    OCAP_EXPORTER_SAVEMESSAGE = [] spawn {
                        while { OCAP_EXPORTER_SAVING } do {
                            hintSilent "Saving...";
                            sleep 1;
                        };
                    };
                };

                if (_data isEqualTo "SAVE FINISHED") exitWith {
                    OCAP_EXPORTER_SAVING = false;
                    terminate OCAP_EXPORTER_SAVEMESSAGE;
                    hintSilent "Saving finished!";
                };
            };

            if (_function isEqualTo "saveResult") exitWith {
                [] spawn {
                    sleep 1;
                    systemChat format["[%1]: %2", OCAP_EXPORTER_ADDON, _data];
                };
            };

            if (_function isEqualTo "error") exitWith {
                if (!isNil "OCAP_EXPORTER_SAVEMESSAGE") then {
                    terminate OCAP_EXPORTER_SAVEMESSAGE;
                };
                OCAP_EXPORTER_SAVING = false;
                [] spawn {
                    sleep 1;
                    systemChat format["[%1]: %2", OCAP_EXPORTER_ADDON, _data];
                    hint format["%1", _data];
                };
            };
        }];
    };

    // define metadata structure
    OCAP_EXPORTER_METADATA = createHashMapFromArray [
        ["attribution", ""],
        ["addonUrl", ""],
        ["displayName", ""],
        ["worldname", ""],
        ["worldName", ""],
        ["worldNameOriginal", ""],
        ["worldSize", 0],
        ["cellSize", 0],
        ["imageSize", 16384],
        ["maxZoom", 6],
        ["multiplier", 1],
        ["hasTopo", true],
        ["hasTopoDark", false],
        ["hasTopoRelief", false],
        ["hasColorRelief", false],
        ["latitude", 0],
        ["longitude", 0]
    ];

    private _worldName = toLower worldName;
    OCAP_EXPORTER_METADATA set ["worldName", _worldName];
    OCAP_EXPORTER_METADATA set ["worldname", _worldName];
    OCAP_EXPORTER_METADATA set ["worldNameOriginal", worldName];

    comment "For worlds larger than the native resolution of the PNG we're going to tile, we'll double the overall resolution of the output. The multiplier should respect this.";
    OCAP_EXPORTER_METADATA set ["worldSize", worldSize];
    private _imageSize = [
        16384,
        32768
    ] select (worldSize >= 16384);
    OCAP_EXPORTER_METADATA set ["imageSize", _imageSize];

    private _multiplier = [
        16384 / worldSize,
        32768 / worldSize
    ] select (worldSize >= 16384);
    OCAP_EXPORTER_METADATA set ["multiplier", _multiplier toFixed 7];

    comment "fetch world data";
    OCAP_EXPORTER_METADATA set ["attribution", getText(configFile >> "CfgWorlds" >> worldName >> "author")];
    OCAP_EXPORTER_METADATA set ["displayName", getText(configFile >> "CfgWorlds" >> worldName >> "description")];
    OCAP_EXPORTER_METADATA set ["latitude", getNumber(configFile >> "CfgWorlds" >> worldName >> "latitude")];
    OCAP_EXPORTER_METADATA set ["longitude", getNumber(configFile >> "CfgWorlds" >> worldName >> "longitude")];

    // waterTexture = "#(argb,8,8,3)color(0.35,0.47,0.66,1)";
    private _waterTexture = (configFile >> "CfgWorlds" >> worldName >> "waterTexture") call BIS_fnc_getCfgData;



    private _mapSource = configSourceMod (configfile >> "CfgWorlds" >> worldName);
    private _mapAddonSearch = getLoadedModsInfo select { _x#1 == _mapSource};
    if (count _mapAddonSearch isNotEqualTo 0) then {
        private _mapAddon = _mapAddonSearch#0;
        private _mapAddonId = _mapAddon#7;
        private _isOfficial = _mapAddon#3;
        private _addonBaseUrl = ["https://steamcommunity.com/workshop/filedetails/?id=","https://store.steampowered.com/app/"] select _isOfficial;
        if (_mapAddonId != 0) then {
            OCAP_EXPORTER_METADATA set ["addonUrl", format ["%1%2", _addonBaseUrl, _mapAddonId]];
        };
    };


    getTerrainInfo params ["_landGridWidth", "_landGridSize", "_terrainGridWidth", "_terrainGridSize", "_seaLevel"];

    OCAP_EXPORTER_METADATA set ["cellSize", _terrainGridWidth];

    comment "Tell the extension we're ready to write - create the folder for the SVG too.";
    private _result = OCAP_EXPORTER_ADDON callExtension [
        "startWriting",
        [_worldName]
    ];
    diag_log text format["[%1]: %2", OCAP_EXPORTER_ADDON, _result#0];
    format["[%1]: %2", OCAP_EXPORTER_ADDON, _result#0] call OCAP_EXPORTER_fnc_log;

    comment "SAVE SVG OF MAP";
    comment "check if running diagnostic version of Arma 3";
    if (isNil "BIS_fnc_diagRadio") exitWith {
        format["[%1]: Exporting the SVG requires running the diagnostics (Development branch) of Arma 3. Please change this under the Properties of Arma 3 in Steam, then relaunch.", OCAP_EXPORTER_ADDON] call OCAP_EXPORTER_fnc_log;
    };

    isNil {
        private _svgPath = format[
            "%1\ocap_exporter\%2\%3.svg",
            (OCAP_EXPORTER_ADDON callExtension "getDir"),
            toLower worldName,
            toLower worldName
        ];
        diag_exportTerrainSVG [_svgPath,true,false,true,true,true,false];
    };

    comment "// filePath
    // locationNames
    // drawGrid
    // drawCountlines
    // drawTreeObjects
    // drawMountainHeightpoints
    // simpleRoads
    ";

    comment "START WRITING HEIGHTMAP";

    comment 'startLoadingScreen ["Exporting..."];';
    startLoadingScreen ["Exporting..."];

    comment "cell size
    _threshold = 8192;
    _count = 0;
    _worldSize = worldSize;
    _divisor = 0;
    while { _divisor == 0 } do {
    	_count = _count + 1;

    	_segments = _worldSize / _count;
    	_remainder = _worldSize mod _count;

    	if ((_segments <= _threshold) && (_remainder == 0)) then {
    		_divisor = _count;
    	};
    };
    ";


    {
        systemChat _x;
        diag_log text _x;
        _x call OCAP_EXPORTER_fnc_log;
    } forEach [
        format["[%1]: World Name: %2 <%3>", OCAP_EXPORTER_ADDON, OCAP_EXPORTER_METADATA get "displayName", _worldName],
        format["[%1]: Cell size: %2", OCAP_EXPORTER_ADDON, _terrainGridWidth],
        format["[%1]: Width/Height: %2", OCAP_EXPORTER_ADDON, _terrainGridSize]
    ];



    comment "
    _divisor = 5;
    ((worldSize / _divisor) + 1) should be used for the Width/Height fields in XML
    ";

    for "_y" from (worldSize - 1) to 0 step (-_terrainGridWidth) do {
        comment '
            hintSilent format ["Row %1/%2", _terrainGridSize - _y, _terrainGridSize];
        ';


        comment "asc";
        private _row = [];

        for "_x" from 0 to (worldSize - 1) step _terrainGridWidth do {
            comment "asc";
            _row pushBack ((getTerrainHeightASL [_x, _y]) toFixed 3);

            comment "capture xyz";
            comment '
                _result = OCAP_EXPORTER_ADDON callExtension [
                    "writeLine",
                    [
                        format [
                            "%1 %2 %3",
                            _x,
                            _y,
                            (getTerrainHeightASL [_x, _y]) toFixed 3
                        ]
                    ]
                ];
            ';
            comment '
            diag_log formatText["%1", _result#0]
            ';
        };
        comment "asc";
        _result = OCAP_EXPORTER_ADDON callExtension [
            "writeAsc",
            [_row joinString " "]
        ];

        comment "hint str _result;";

        comment 'progressLoadingScreen (_y / _terrainGridSize);';
        progressLoadingScreen (100 - (_y / worldSize));
    };

    comment 'endLoadingScreen;';
    endLoadingScreen;

    private _metadataJson = [OCAP_EXPORTER_METADATA] call CBA_fnc_encodeJSON;

    OCAP_EXPORTER_ADDON callExtension [
        "finishWriting",
        [
            _metadataJson
        ]
    ];

};