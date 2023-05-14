package main

/*
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "extensionCallback.h"
*/
import "C" // This is required to import the C code

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
	"time"
	"unsafe"
)

var EXTENSION_VERSION string = "0.0.1"
var extensionCallbackFnc C.extensionCallback

var ARMA3_ROOT string = getDir()
var ADDON string = "ocap_exporter"
var EXPORT_FOLDER string = ARMA3_ROOT + "\\" + ADDON

var WORLDNAME string
var EXPORT_WORLD_FOLDER string
var HEIGHTMAP_FILE_PATH string
var HEIGHTMAP_FILE *os.File
var HEIGHTMAP_DATA []string
var METADATA_FILE_PATH string
var METADATA_FILE *os.File
var LOG_FILE_PATH string
var LOG_FILE *os.File

func version() string {
	return EXTENSION_VERSION
}

func getDir() string {
	dir, err := os.Getwd()
	if err != nil {
		log.Fatal(err)
	}
	return dir
}

//export goRVExtensionVersion
func goRVExtensionVersion(output *C.char, outputsize C.size_t) {
	result := C.CString(EXTENSION_VERSION)
	defer C.free(unsafe.Pointer(result))
	var size = C.strlen(result) + 1
	if size > outputsize {
		size = outputsize
	}
	C.memmove(unsafe.Pointer(output), unsafe.Pointer(result), size)
}

//export goRVExtensionArgs
func goRVExtensionArgs(output *C.char, outputsize C.size_t, input *C.char, argv **C.char, argc C.int) {
	var offset = unsafe.Sizeof(uintptr(0))
	var out []string
	for index := C.int(0); index < argc; index++ {
		out = append(out, C.GoString(*argv))
		argv = (**C.char)(unsafe.Pointer(uintptr(unsafe.Pointer(argv)) + offset))
	}

	// temp := fmt.Sprintf("Function: %s nb params: %d params: %s!", C.GoString(input), argc, out)
	temp := fmt.Sprintf("Function: %s nb params: %d", C.GoString(input), argc)

	switch C.GoString(input) {
	case "log":
		{
			if argc == 1 {
				logFromArma(out[0])
			}
		}
	case "startWriting":
		{
			if argc == 1 {
				temp = startWriting(out[0])
			}
		}
	case "writeLine":
		{
			if argc == 1 {
				writeLine(&out)
				temp = "Writing data..."
			}
		}
	case "finishWriting":
		{
			if argc == 1 {
				finishWriting(&out)
				temp = "Saving data..."
			}
		}
	}

	// Return a result to Arma
	result := C.CString(temp)
	defer C.free(unsafe.Pointer(result))
	var size = C.strlen(result) + 1
	if size > outputsize {
		size = outputsize
	}

	C.memmove(unsafe.Pointer(output), unsafe.Pointer(result), size)
}

func trimQuotes(s string) string {
	// trim the start and end quotes from a string
	return strings.Trim(s, `"`)
}

func fixEscapeQuotes(s string) string {
	// fix the escape quotes in a string
	return strings.Replace(s, `""`, `"`, -1)
}

func startWriting(worldname string) string {
	var err error

	// create export folder
	_, err = os.Stat(EXPORT_FOLDER)
	if os.IsNotExist(err) {
		os.Mkdir(EXPORT_FOLDER, 0755)
	}

	// create world subfolder
	WORLDNAME = fixEscapeQuotes(trimQuotes(worldname))
	EXPORT_WORLD_FOLDER = EXPORT_FOLDER + "\\" + WORLDNAME
	HEIGHTMAP_FILE_PATH = EXPORT_WORLD_FOLDER + "\\" + WORLDNAME + ".asc"
	HEIGHTMAP_DATA = []string{}
	METADATA_FILE_PATH = EXPORT_WORLD_FOLDER + "\\" + "map.json"
	LOG_FILE_PATH = EXPORT_WORLD_FOLDER + "\\" + ADDON + ".log"

	// create world subfolder
	_, err = os.Stat(EXPORT_WORLD_FOLDER)
	if os.IsNotExist(err) {
		os.Mkdir(EXPORT_WORLD_FOLDER, 0755)
	} else {
		// delete existing world subfolder and any contents
		os.RemoveAll(EXPORT_WORLD_FOLDER)
		// create world subfolder
		os.Mkdir(EXPORT_WORLD_FOLDER, 0755)
	}

	// define log output
	LOG_FILE, err = os.OpenFile(LOG_FILE_PATH, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
	if err != nil {
		errStr := fmt.Sprintf(`Error creating log file: %s`, err)
		log.Println(errStr)
		logCallback("error", errStr)
		return errStr
	}
	log.SetOutput(LOG_FILE)
	// set format
	log.SetFlags(log.Ldate | log.Ltime)

	// create heightmap file
	// HEIGHTMAP_FILE, err = os.OpenFile(HEIGHTMAP_FILE_PATH, os.O_CREATE|os.O_WRONLY, 0644)
	// if err != nil {
	// 	errStr := fmt.Sprintf(`Error creating heightmap file: %s`, err)
	// 	log.Println(errStr)
	// 	logCallback("error", errStr)
	// 	return errStr
	// }
	// HEIGHTMAP_FILE.Close()

	// METADATA_FILE, err = os.Create(METADATA_FILE_PATH)
	// if err != nil {
	// 	errStr := fmt.Sprintf(`Error creating metadata file: %s`, err)
	// 	log.Println(errStr)
	// 	logCallback("error", errStr)
	// 	return errStr
	// }
	// METADATA_FILE.Close()

	// return `Output files created`
	return "Logging started"
}

func writeLine(args *[]string) {
	HEIGHTMAP_DATA = append(HEIGHTMAP_DATA, fixEscapeQuotes(trimQuotes((*args)[0])))
}

func finishWriting(args *[]string) {
	var err error

	logCallback("finishWriting", "SAVE STARTED")

	// remove file handles if they exist
	if HEIGHTMAP_FILE != nil {
		HEIGHTMAP_FILE.Close()
	}
	if METADATA_FILE != nil {
		METADATA_FILE.Close()
	}

	metadata := (*args)[0]

	// parse metadata from stringified json
	var metadataMap map[string]interface{}
	metadata = fixEscapeQuotes(trimQuotes(metadata))
	log.Println(metadata)
	json.Unmarshal([]byte(metadata), &metadataMap)

	// multiplier is a string value from Arma to avoid scientific notation. Convert to number.
	multiplier := metadataMap["multiplier"].(string)
	// convert to float64
	multiplierFloat, err := strconv.ParseFloat(multiplier, 64)
	if err != nil {
		errStr := fmt.Sprintf(`Error parsing multiplier: %s`, err)
		log.Println(errStr)
		logCallback("error", errStr)
		return
	}
	// save to metadata map
	metadataMap["multiplier"] = multiplierFloat

	log.Println("=== Writing metadata ===")

	// open metadata file
	METADATA_FILE, err = os.OpenFile(METADATA_FILE_PATH, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		errStr := fmt.Sprintf(`Error opening metadata file: %s`, err)
		log.Println(errStr)
		logCallback("error", errStr)
		return
	}

	// write metadata to file
	log.Println("Prettifying JSON...")
	encoder := json.NewEncoder(METADATA_FILE)
	encoder.SetIndent("", "    ")
	log.Println("Writing data...")
	err = encoder.Encode(metadataMap)
	if err != nil {
		errStr := fmt.Sprintf(`Error writing metadata: %s`, err)
		log.Println(errStr)
		logCallback("error", errStr)
		return
	}
	METADATA_FILE.Close()

	log.Println("=== Writing heightmap ===")

	// open heightmap file
	HEIGHTMAP_FILE, err = os.OpenFile(HEIGHTMAP_FILE_PATH, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		errStr := fmt.Sprintf(`Error opening heightmap file: %s`, err)
		log.Println(errStr)
		logCallback("error", errStr)
		return
	}

	log.Println("Writing asc file header...")
	// convert to strings
	worldSize := metadataMap["worldSize"].(float64)
	worldSizeStr := fmt.Sprintf(`%f`, metadataMap["worldSize"].(float64))
	cellSize := metadataMap["cellSize"].(float64)
	cellSizeStr := fmt.Sprintf(`%f`, metadataMap["cellSize"].(float64))

	cols := worldSize / cellSize
	// convert to int
	colsInt := int(cols)

	log.Println("worldSize: " + worldSizeStr)
	log.Println("cellSize: " + cellSizeStr)
	HEIGHTMAP_FILE.WriteString(fmt.Sprintf(`ncols %d`, colsInt) + "\n")
	HEIGHTMAP_FILE.WriteString(fmt.Sprintf(`nrows %d`, colsInt) + "\n")
	HEIGHTMAP_FILE.WriteString("xllcorner 0\n")
	HEIGHTMAP_FILE.WriteString("yllcorner 0\n")
	HEIGHTMAP_FILE.WriteString("cellsize " + cellSizeStr + "\n")
	HEIGHTMAP_FILE.WriteString("NODATA_value -9999\n")

	log.Println("Writing asc file data...")
	for _, line := range HEIGHTMAP_DATA {
		_, err = HEIGHTMAP_FILE.Write([]byte(line + "\n")[:])
		if err != nil {
			errStr := fmt.Sprintf(`Error writing heightmap: %s`, err)
			log.Println(errStr)
			logCallback("error", errStr)
			return
		}
	}
	HEIGHTMAP_FILE.Close()

	logCallback("finishWriting", "SAVE FINISHED")
	time.Sleep(500 * time.Millisecond)
	logCallback("saveResult", fmt.Sprintf(`Wrote heightmap: %s`, HEIGHTMAP_FILE_PATH))
	time.Sleep(500 * time.Millisecond)
	logCallback("saveResult", fmt.Sprintf(`Wrote metadata: %s`, METADATA_FILE_PATH))

}

func logCallback(functionName string, data string) {
	statusName := C.CString(ADDON)
	defer C.free(unsafe.Pointer(statusName))
	statusFunction := C.CString(functionName)
	defer C.free(unsafe.Pointer(statusFunction))
	statusParam := C.CString(data)
	defer C.free(unsafe.Pointer(statusParam))
	runExtensionCallback(statusName, statusFunction, statusParam)

	log.Printf(`%s: %s`, functionName, data)
}

func logFromArma(message string) {
	log.Println(fixEscapeQuotes(trimQuotes(message)))
}

//export goRVExtension
func goRVExtension(output *C.char, outputsize C.size_t, input *C.char) {

	var temp string

	// logLine("goRVExtension", fmt.Sprintf(`["Input: %s",  "DEBUG"]`, C.GoString(input)), true)

	switch C.GoString(input) {
	case "version":
		temp = EXTENSION_VERSION
	case "getDir":
		temp = getDir()
	default:
		temp = "Unknown Function"
	}

	result := C.CString(temp)
	defer C.free(unsafe.Pointer(result))
	var size = C.strlen(result) + 1
	if size > outputsize {
		size = outputsize
	}

	C.memmove(unsafe.Pointer(output), unsafe.Pointer(result), size)
	// return
}

func runExtensionCallback(name *C.char, function *C.char, data *C.char) C.int {
	return C.runExtensionCallback(extensionCallbackFnc, name, function, data)
}

//export goRVExtensionRegisterCallback
func goRVExtensionRegisterCallback(fnc C.extensionCallback) {
	extensionCallbackFnc = fnc
}

func main() {}
