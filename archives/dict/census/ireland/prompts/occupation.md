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

// Complete comprehensive correction for batch 10
import Papa from 'papaparse';
const fileContent = await window.fs.readFile('ire_occupation_1901.csv', { encoding: 'utf8' });

const parsedData = Papa.parse(fileContent, {
header: true,
skipEmptyLines: true,
delimitersToGuess: [',', '\t', '|', ';']
});

const batch10Data = parsedData.data.slice(2700, 3000);

function correctOccupationComprehensive(occupation) {
if (!occupation) return '';

    let corrected = occupation.trim();
    corrected = corrected.replace(/[\[\]()]/g, '');
    corrected = corrected.replace(/-/g, ' ');
    corrected = corrected.replace(/\s+/g, ' ').trim();

    const corrections = {
        // All comprehensive corrections from previous batches
        "Farmers Mother in Law": "Farmer's Mother in Law", "Fishermans Wife": "Fisherman's Wife",
        "Labouer General": "General Labourer", "General Laburer": "General Labourer", 
        "Accountants Clerk": "Accountant's Clerk", "Blacksmiths Apprentice": "Blacksmith's Apprentice",
        "Agricultural Labourers Daughter": "Agricultural Labourer's Daughter", "Printers Labourer": "Printer's Labourer",
        "Chemists Apprentice": "Chemist's Apprentice", "Brewers Clerk": "Brewer's Clerk", "Shoemakers Wife": "Shoemaker's Wife",

        // Compound words
        "House Keeper": "Housekeeper", "Shop Keeper": "Shopkeeper", "Watch Maker": "Watchmaker",
        "Shoe Maker": "Shoemaker", "Dress Maker": "Dressmaker", "Black Smith": "Blacksmith", 
        "Post Man": "Postman", "House Maid": "Housemaid", "Silver Smith": "Silversmith", 
        "Coach Man": "Coachman", "Wheel Wright": "Wheelwright", "Watch Man": "Watchman", 
        "House Work": "Housework", "Book Keeper": "Bookkeeper",

        // All other established corrections
        "Farmers Son": "Farmer's Son", "Farmers Daughter": "Farmer's Daughter", "Farmers Wife": "Farmer's Wife",
        "Labourers Wife": "Labourer's Wife", "Tailors Wife": "Tailor's Wife", "Policemans Son": "Policeman's Son",
        "Policemans Wife": "Policeman's Wife", "Shop Keepers Wife": "Shopkeeper's Wife", 
        "Shopkeepers Daughter": "Shopkeeper's Daughter", "Caretakers Wife": "Caretaker's Wife",
        "Publicans Wife": "Publican's Wife", "Blacksmiths Helper": "Blacksmith's Helper",
        "Childrens Nurse": "Children's Nurse", "Sailors Wife": "Sailor's Wife",
        "General Servant Domestic": "General Domestic Servant", "Servant Domestic": "Domestic Servant",
        "Labourer General": "General Labourer", "Labourer Agricultural": "Agricultural Labourer",
        "Cleark": "Clerk", "Plummer": "Plumber", "Salior": "Sailor", "Serveant": "Servant",
        "Schol": "Scholar", "Schloar": "Scholar", "At Shool": "At School", 
        "Labours": "Labourer", "Laburer": "Labourer", "Gen Laborer": "Gen Labourer"
    };

    return corrections[corrected] || corrected;
}

const correctedBatch10Final = batch10Data.map(row => ({
occupation: row.occupation,
count: row.count,
corrected_occupation: correctOccupationComprehensive(row.occupation)
}));

// Show all corrections
console.log("COMPREHENSIVE BATCH 10 CORRECTIONS:");
let finalChangeCount = 0;
for (let i = 0; i < correctedBatch10Final.length; i++) {
const row = correctedBatch10Final[i];
if (row.occupation !== row.corrected_occupation) {
finalChangeCount++;
console.log(`${2700+i+1}. "${row.occupation}" → "${row.corrected_occupation}" ✓`);
}
}

console.log(`\nFinal comprehensive total: ${finalChangeCount} out of ${correctedBatch10Final.length} entries`);

// Generate CSV
const batch10CSV = Papa.unparse(correctedBatch10Final);
console.log("\n" + "=".repeat(80));
console.log("BATCH 10 COMPREHENSIVE CSV (300 ROWS):");
console.log("=".repeat(80));
console.log(batch10CSV);