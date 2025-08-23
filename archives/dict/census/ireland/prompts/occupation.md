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

// Complete the batch 9 processing
import Papa from 'papaparse';
const fileContent = await window.fs.readFile('ire_occupation_1901.csv', { encoding: 'utf8' });

const parsedData = Papa.parse(fileContent, {
header: true,
skipEmptyLines: true,
delimitersToGuess: [',', '\t', '|', ';']
});

const batch9Data = parsedData.data.slice(2400, 2700);

function correctOccupationStage2(occupation) {
if (!occupation) return '';

    let corrected = occupation.trim();
    corrected = corrected.replace(/[\[\]()]/g, '');
    corrected = corrected.replace(/-/g, ' ');
    corrected = corrected.replace(/\s+/g, ' ').trim();

    const corrections = {
        // Comprehensive corrections from previous batches
        "Farmers Son": "Farmer's Son", "Farmers Daughter": "Farmer's Daughter", "Farmers Wife": "Farmer's Wife",
        "Labourers Wife": "Labourer's Wife", "Labourers Daughter": "Labourer's Daughter", "Labourers Son": "Labourer's Son",
        "Tailors Daughter": "Tailor's Daughter", "Tailors Wife": "Tailor's Wife", "Policemans Son": "Policeman's Son",
        "Policemans Wife": "Policeman's Wife", "Shopkeepers Daughter": "Shopkeeper's Daughter", 
        "Shopkeepers Son": "Shopkeeper's Son", "Shop Keepers Daughter": "Shopkeeper's Daughter",
        "Shop Keepers Wife": "Shopkeeper's Wife", "Fishermans Daughter": "Fisherman's Daughter",
        "Childrens Nurse": "Children's Nurse", "Childrens Maid": "Children's Maid", "Sailors Wife": "Sailor's Wife",
        "Caretakers Wife": "Caretaker's Wife", "Caretakers Daughter": "Caretaker's Daughter",
        "Publicans Wife": "Publican's Wife", "Publicans Son": "Publican's Son", "Publicans Daughter": "Publican's Daughter",
        "Land Agents Assistant": "Land Agent's Assistant", "Blacksmiths Assistant": "Blacksmith's Assistant",
        "Butchers Assistant": "Butcher's Assistant", "Carpenters Wife": "Carpenter's Wife",

        // Compound words
        "House Keeper": "Housekeeper", "Shop Keeper": "Shopkeeper", "Clock Maker": "Clockmaker",
        "Watch Maker": "Watchmaker", "Shoe Maker": "Shoemaker", "Dress Maker": "Dressmaker",
        "Black Smith": "Blacksmith", "Post Man": "Postman", "House Maid": "Housemaid",

        // Servant standardization  
        "General Servant Domestic": "General Domestic Servant", "Gen Servant Domestic": "General Domestic Servant",
        "Servant Domestic": "Domestic Servant", "Domestic servant": "Domestic Servant",

        // Spelling corrections
        "Cleark": "Clerk", "Plummer": "Plumber", "Salior": "Sailor", "Machanist": "Machinist",
        "Schol": "Scholar", "At Shool": "At School", "Labours": "Labourer", "Hous Wife": "House Wife",
        "Farms Servant": "Farm Servant"
    };

    if (corrections[corrected]) {
        corrected = corrections[corrected];
    }
    return corrected;
}

const correctedBatch9Final = batch9Data.map(row => ({
occupation: row.occupation,
count: row.count,
corrected_occupation: correctOccupationStage2(row.occupation)
}));

// Show corrections
console.log("FINAL BATCH 9 CORRECTIONS:");
let finalChangeCount = 0;
for (let i = 0; i < correctedBatch9Final.length; i++) {
const row = correctedBatch9Final[i];
if (row.occupation !== row.corrected_occupation) {
finalChangeCount++;
console.log(`${2400+i+1}. "${row.occupation}" → "${row.corrected_occupation}" ✓`);
}
}

console.log(`\nFinal total corrections: ${finalChangeCount} out of ${correctedBatch9Final.length} entries`);

// Generate final CSV
const batch9CSV = Papa.unparse(correctedBatch9Final);
console.log("\n" + "=".repeat(80));
console.log("FINAL BATCH 9 CSV OUTPUT (300 ROWS):");
console.log("=".repeat(80));
console.log(batch9CSV);