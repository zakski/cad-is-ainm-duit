Do Batch Processing of the attached csv file to correct and standardise the spelling and grammar in the occupation column.

The context of the data is occupations listed in the 1901 Irish Census, by descending frequency.

The file will have a header and 2 columns. Keep the original columns in place, and the ordering of the file intact. Do not sort the file.

This is how I want you to process the occupation column.

First remove any brackets, handle '-' as whitespace, then condense duplicate whitespace.

Next fix the spelling and grammar according to British English, make sure apostrophes are added where appropriate, standardise the word ordering, and expand abbreviations. Where words can be combined, e.g. House Keeper to Housekeeper, please do so.

Store the results of your corrections in a 3rd column called "corrected_occupation".

Please return the resulting csv file to me in batches of exactly 300 lines.

I have attached a script you already created to do this.

Please start from batch 7. do the batches one at a time. review batch 7 for word ordering and spelling.

// STAGE 2: Complete reprocess with enhanced corrections
import Papa from 'papaparse';
const fileContent = await window.fs.readFile('ire_occupation_1901.csv', { encoding: 'utf8' });

const parsedData = Papa.parse(fileContent, {
header: true,
skipEmptyLines: true,
delimitersToGuess: [',', '\t', '|', ';']
});

// Enhanced Stage 2 correction function
function correctOccupationStage2(occupation) {
if (!occupation) return '';

    let corrected = occupation.trim();

    // ENHANCED PREPROCESSING
    corrected = corrected.replace(/[\[\]()]/g, '');
    corrected = corrected.replace(/-/g, ' ');
    corrected = corrected.replace(/\s+/g, ' ').trim();

    // COMPREHENSIVE CORRECTIONS (Stage 1 + Stage 2 additions)
    const corrections = {
        // All Stage 1 apostrophe corrections
        "Farmers Son": "Farmer's Son",
        "Farmers Daughter": "Farmer's Daughter",
        "Farmers Wife": "Farmer's Wife",
        "Farmer Son": "Farmer's Son",
        "Farmer Daughter": "Farmer's Daughter",
        "Farmers Sister": "Farmer's Sister",
        "Farmers Brother": "Farmer's Brother",
        "Farmers Nephew": "Farmer's Nephew",
        "Farmers Niece": "Farmer's Niece",
        "Farmers Mother": "Farmer's Mother",
        "Farmers Widow": "Farmer's Widow",
        "Farmers Servant": "Farmer's Servant",
        "Farmers Labourer": "Farmer's Labourer",
        "Farmers Assistant": "Farmer's Assistant",
        "Labourers Wife": "Labourer's Wife",
        "Labourers Daughter": "Labourer's Daughter",
        "Labourers Son": "Labourer's Son",
        "Labourers Widow": "Labourer's Widow",
        "Blacksmiths Assistant": "Blacksmith's Assistant",
        "Butchers Assistant": "Butcher's Assistant",
        "Tailors Assistant": "Tailor's Assistant",
        "Shoemakers Assistant": "Shoemaker's Assistant",
        "Carpenters Assistant": "Carpenter's Assistant",
        "Drapers Assistant": "Draper's Assistant",
        "Grocers Assistant": "Grocer's Assistant",
        "Bakers Assistant": "Baker's Assistant",
        "Soldiers Wife": "Soldier's Wife",
        "Policemans Son": "Policeman's Son",
        "Policemans Wife": "Policeman's Wife",
        "Teachers Daughter": "Teacher's Daughter",
        "Tailors Wife": "Tailor's Wife",
        "Carpenters Wife": "Carpenter's Wife",
        "Carpenters Son": "Carpenter's Son",
        "Carpenters Daughter": "Carpenter's Daughter",
        "Shepherds Son": "Shepherd's Son",
        "Shepherds Daughter": "Shepherd's Daughter",
        "Shepherds Wife": "Shepherd's Wife",
        "Herds Son": "Herd's Son",
        "Herds Daughter": "Herd's Daughter",
        "Herds Wife": "Herd's Wife",
        "Publicans Son": "Publican's Son",
        "Publicans Daughter": "Publican's Daughter",
        "Publicans Wife": "Publican's Wife",
        "Publicans Assistant": "Publican's Assistant",
        "Shopkeepers Son": "Shopkeeper's Son",
        "Shopkeepers Daughter": "Shopkeeper's Daughter",
        "Shop Keepers Daughter": "Shopkeeper's Daughter",
        "Shop Keepers Wife": "Shopkeeper's Wife",
        "Dairymans Son": "Dairyman's Son",
        "Dairymans Daughter": "Dairyman's Daughter",
        "Mill Owners Wife": "Mill Owner's Wife",
        "Fishermans Daughter": "Fisherman's Daughter",
        "Childrens Nurse": "Children's Nurse",
        "Sailors Wife": "Sailor's Wife",
        "Famers Son": "Farmer's Son",
        "Farmers' Son": "Farmer's Son",
        
        // NEW STAGE 2 CORRECTIONS identified from analysis
        "Shepherd Son": "Shepherd's Son",
        "Herd Daughter": "Herd's Daughter", 
        "Tailors Daughter": "Tailor's Daughter",
        "Famers Daughter": "Farmer's Daughter",
        "Caretakers Daughter": "Caretaker's Daughter",
        "Farmeress Son": "Farmeress's Son",
        "Farmeress Daughter": "Farmeress's Daughter",
        "Labrs Wife": "Labourer's Wife",

        // Compound words
        "House Keeper": "Housekeeper",
        "Shop Keeper": "Shopkeeper",
        "Gate Keeper": "Gatekeeper",
        "Time Keeper": "Timekeeper",
        "Care Taker": "Caretaker",
        "Watch Maker": "Watchmaker",
        "Clock Maker": "Clockmaker",
        "Shoe Maker": "Shoemaker",
        "Dress Maker": "Dressmaker",
        "Cabinet Maker": "Cabinetmaker",
        "Stone Mason": "Stonemason",
        "Black Smith": "Blacksmith",
        "Post Man": "Postman",
        "Police Man": "Policeman",
        "Milk Man": "Milkman",
        "Bar Maid": "Barmaid",
        "House Maid": "Housemaid",
        "Boot Maker": "Bootmaker",
        "Hair Dresser": "Hairdresser",
        "Station Master": "Stationmaster",
        "Post Master": "Postmaster",
        "Brick Layer": "Bricklayer",
        "Coach Man": "Coachman",
        "Fisher Man": "Fisherman",
        "Market Gardner": "Market Gardener",
        "Iron Monger": "Ironmonger",

        // Servant standardization
        "General Servant Domestic": "General Domestic Servant",
        "Gen Servant Domestic": "General Domestic Servant",
        "Genl Servant Domestic": "General Domestic Servant",
        "Servant Domestic": "Domestic Servant",
        "Domestic Servt": "Domestic Servant",
        "Domestic servant": "Domestic Servant",

        // Order corrections
        "Labourer General": "General Labourer",
        "Labourer Agricultural": "Agricultural Labourer",

        // Common spelling
        "Cleark": "Clerk",
        "Clarke": "Clerk",
        "Plumer": "Plumber",
        "Shomaker": "Shoemaker",
        "Miliner": "Milliner",
        "Laundres": "Laundress",
        "Aprentice": "Apprentice",
        "Serveant": "Servant",

        // Labourer variants
        "Labours": "Labourer",
        "Labiour": "Labourer",
        "Labrourer": "Labourer",

        // Machinist
        "Machinest": "Machinist",
        "Machineist": "Machinist"
    };

    if (corrections[corrected]) {
        corrected = corrections[corrected];
    }

    return corrected;
}

// Process batch 8 (rows 2100-2400) with Stage 2 corrections
const batch8Data = parsedData.data.slice(2100, 2400);
console.log(`STAGE 2 FINAL: Processing batch 8: rows 2101-2400 (${batch8Data.length} rows)`);

const correctedBatch8Final = batch8Data.map(row => ({
occupation: row.occupation,
count: row.count,
corrected_occupation: correctOccupationStage2(row.occupation)
}));

// Show all final corrections
console.log("\nFINAL BATCH 8 CORRECTIONS:");
let finalChangeCount = 0;
for (let i = 0; i < correctedBatch8Final.length; i++) {
const row = correctedBatch8Final[i];
if (row.occupation !== row.corrected_occupation) {
finalChangeCount++;
console.log(`${2100+i+1}. "${row.occupation}" → "${row.corrected_occupation}" ✓`);
}
}

console.log(`\nFinal total corrections: ${finalChangeCount} out of ${correctedBatch8Final.length} entries`);

// Generate final CSV
const batch8CSV = Papa.unparse(correctedBatch8Final);
console.log("\n" + "=".repeat(80));
console.log("FINAL BATCH 8 CSV OUTPUT (300 ROWS):");
console.log("=".repeat(80));
console.log(batch8CSV);