#target photoshop

// === ADD .trim() SUPPORT FOR OLDER ExtendScript ===
if (typeof String.prototype.trim !== 'function') {
    String.prototype.trim = function () {
        return this.replace(/^\s+|\s+$/g, '');
    };
}

var scriptFile = new File($.fileName);
var scriptDir = scriptFile.path;

var templatePath = scriptDir + "/Poker Cards (2-5x3-5) 18 per sheet.psd";
var imageFolder = new Folder(scriptDir + "/Cards_resized");
var outputFolder = new Folder(scriptDir + "/output_sheets");
var cardListFile = File(scriptDir + "/cardlist.txt");

// === CONFIGURATION FOR BACKS ===
var imageFolderBacks = new Folder(scriptDir + "/Cardbacks_resized");
var outputFolderBacks = new Folder(scriptDir + "/output_sheets/output_sheets_backs");
var cardListFileBacks = File(scriptDir + "/cardlistback.txt");

function Sheets(templatePath, imageFolder, outputFolder, cardListFile) {
    if (!outputFolder.exists) {
        outputFolder.create(); // Create folder if it doesn't exist
    }

    // === GRID POSITIONS ===
    var xCoords = [118, 1243, 2369];
    var yCoords = [229, 1054, 1880, 2710, 3532, 4361];

    var gridPositions = [];
    for (var y = 0; y < yCoords.length; y++) {
        for (var x = 0; x < xCoords.length; x++) {
            gridPositions.push({ x: xCoords[x], y: yCoords[y] });
        }
    }

    // === READ CARD LIST ===
    var cardNames = [];

    if (cardListFile.exists) {
        cardListFile.open("r");
        while (!cardListFile.eof) {
            var line = cardListFile.readln();
            if (line !== undefined && line !== null) {
                line = String(line).trim();
                if (line !== "") {
                    cardNames.push(line);
                }
            }
        }
        cardListFile.close();
    } else {
        alert("Card list file not found.");
        throw new Error("cardlist.txt missing");
    }

    // === SCRIPT START ===
    var sheetCount = 1;
    var imageIndex = 0;

    while (imageIndex < cardNames.length) {
        var templateDoc = app.open(new File(templatePath));
        var placedOnThisSheet = 0;

        while (placedOnThisSheet < gridPositions.length && imageIndex < cardNames.length) {
            var cardName = cardNames[imageIndex];
            var foundImage = null;

            // Try common extensions
            var extensions = [".jpg", ".jpeg", ".png"];
            for (var e = 0; e < extensions.length; e++) {
                var tryFile = new File(imageFolder.fsName + "/" + cardName + extensions[e]);
                if (tryFile.exists) {
                    foundImage = tryFile;
                    break;
                }
            }

            if (!foundImage) {
                alert("Image not found for card: " + cardName);
                imageIndex++;
                continue;
            }

            var img = app.open(foundImage);
            img.selection.selectAll();
            img.selection.copy();
            img.close(SaveOptions.DONOTSAVECHANGES);

            app.activeDocument = templateDoc;
            templateDoc.paste();

            var layer = templateDoc.activeLayer;
            var bounds = layer.bounds;
            var currentX = bounds[0].value;
            var currentY = bounds[1].value;

            var targetPos = gridPositions[placedOnThisSheet];
            var dx = targetPos.x - currentX;
            var dy = targetPos.y - currentY;

            var safeName = cardName.replace(/[\\\/:*?"<>|(),]/g, '').replace(/\s+/g, '_');
            layer.translate(dx, dy);
            layer.name = "Image_" + (imageIndex + 1) + "_" + safeName;

            placedOnThisSheet++;
            imageIndex++;
        }

        // Flatten for JPEG
        templateDoc.flatten();

        // Save as JPEG
        var jpgName = new File(outputFolder.fsName + "/Sheet" + sheetCount + ".jpg");
        var jpgOptions = new JPEGSaveOptions();
        jpgOptions.quality = 12;
        jpgOptions.formatOptions = FormatOptions.STANDARDBASELINE;
        jpgOptions.embedColorProfile = true;

        try {
            templateDoc.saveAs(jpgName, jpgOptions, true);
        } catch (e) {
            alert("JPEG save failed:\n" + e.message + "\nPath: " + jpgName.fsName);
        }

        templateDoc.close(SaveOptions.DONOTSAVECHANGES);
        sheetCount++;
    }
    //alert("Finished placing " + cardNames.length + " cards into " + (sheetCount - 1) + " sheet(s).");

}

Sheets(templatePath, imageFolder, outputFolder, cardListFile);
Sheets(templatePath, imageFolderBacks, outputFolderBacks, cardListFileBacks);
// Close all open documents
while (app.documents.length > 0) {
    app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
}

// Optional: create a completion flag file
var doneFile = new File(scriptDir + "/done.flag");
doneFile.open("w");
doneFile.writeln("done");
doneFile.close();

