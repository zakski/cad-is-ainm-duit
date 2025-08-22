Do Batch Processing of the attached csv file to correct and standardise the spelling and grammar in the occupation column.

The context of the data is occupations listed in the 1901 Irish Census, by descending frequency.

The file will have a header and 2 columns. Keep the original columns in place, and the ordering of the file intact. Do not sort the file.

This is how I want you to process the occupation column.

First remove any brackets, handle '-' as whitespace, then condense duplicate whitespace.

Next fix the spelling and grammar according to British English, make sure apostrophes are added where appropriate, standardise the word ordering, and expand abbreviations. Where words can be combined, e.g. House Keeper to Housekeeper, please do so.

Store the results of your corrections in a 3rd column called "corrected_occupation".

Please return the resulting csv file to me in batches of exactly 300 lines.

// Combined script: Best spelling corrections + better bracket/whitespace handling
import Papa from 'papaparse';
const fileContent = await window.fs.readFile('ire_occupation_1901.csv', { encoding: 'utf8' });

const parsedData = Papa.parse(fileContent, {
header: true,
skipEmptyLines: true,
delimitersToGuess: [',', '\t', '|', ';']
});

// Combined correction function with enhanced preprocessing and comprehensive corrections
function correctOccupation(occupation) {
if (!occupation) return '';

    let corrected = occupation.trim();
    
    // ENHANCED PREPROCESSING (from my script)
    // 1. Remove brackets first
    corrected = corrected.replace(/[\[\]()]/g, '');
    
    // 2. Handle hyphens as whitespace
    corrected = corrected.replace(/-/g, ' ');
    
    // 3. Condense duplicate whitespace
    corrected = corrected.replace(/\s+/g, ' ').trim();
    
    // COMPREHENSIVE CORRECTIONS (from your script)
    const corrections = {
        // Apostrophe corrections
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
        
        // Combine compound words
        "House Keeper": "Housekeeper",
        "Book Keeper": "Bookkeeper",
        "Shop Keeper": "Shopkeeper",
        "Gate Keeper": "Gatekeeper",
        "Time Keeper": "Timekeeper",
        "Care Taker": "Caretaker",
        "Watch Maker": "Watchmaker",
        "Clock Maker": "Clockmaker",
        "Shoe Maker": "Shoemaker",
        "Dress Maker": "Dressmaker",
        "Cabinet Maker": "Cabinetmaker",
        "Paper Hanger": "Paperhanger",
        "Stone Mason": "Stonemason",
        "Black Smith": "Blacksmith",
        "Gold Smith": "Goldsmith",
        "Silver Smith": "Silversmith",
        "Tin Smith": "Tinsmith",
        "White Smith": "Whitesmith",
        "Wheel Wright": "Wheelwright",
        "Mill Wright": "Millwright",
        "Ship Wright": "Shipwright",
        "Post Man": "Postman",
        "Police Man": "Policeman",
        "Milk Man": "Milkman",
        "Bar Man": "Barman",
        "Bar Maid": "Barmaid",
        "House Maid": "Housemaid",
        "Rope Maker": "Ropemaker",
        "Lace Maker": "Lacemaker",
        "Boot Maker": "Bootmaker",
        "Hair Dresser": "Hairdresser",
        "News Agent": "Newsagent",
        "Station Master": "Stationmaster",
        "Post Master": "Postmaster",
        "Post Mistress": "Postmistress",
        "Brick Layer": "Bricklayer",
        "Coach Man": "Coachman",
        "Fisher Man": "Fisherman",
        
        // Educational titles
        "School Teacher": "Schoolteacher",
        "National School Teacher": "National Schoolteacher",
        "National School Master": "National Schoolmaster",
        "National School Mistress": "National Schoolmistress",
        "School Master": "Schoolmaster",
        "School Mistress": "Schoolmistress",
        "Hedge School Master": "Hedge Schoolmaster",
        
        // Standardize servant types
        "General Servant Domestic": "General Domestic Servant",
        "Domestic General Servant": "General Domestic Servant",
        "General Servant, Domestic": "General Domestic Servant",
        "Domestic Servant, General": "General Domestic Servant",
        "Domestic Servant General": "General Domestic Servant",
        "General Servt Domestic": "General Domestic Servant",
        "Genl Servant Domestic": "General Domestic Servant",
        "Gen Servant Domestic": "General Domestic Servant",
        "G Servant Domestic": "General Domestic Servant",
        "Servant Domestic": "Domestic Servant",
        "Servant (Domestic)": "Domestic Servant",
        "Domestic Servt": "Domestic Servant",
        "Dom Servant": "Domestic Servant",
        "D Servant": "Domestic Servant",
        "Domestic Servent": "Domestic Servant",
        "Domestic Serveant": "Domestic Servant",
        "Domestick Servant": "Domestic Servant",
        "Domestic servant": "Domestic Servant",
        "Domest Servant": "Domestic Servant",
        
        // American to British spelling corrections
        "Agricultural Laborer": "Agricultural Labourer",
        "Farm Laborer": "Farm Labourer",
        "General Laborer": "General Labourer",
        "Laborer": "Labourer",
        
        // Order corrections for compound occupations
        "Labourer General": "General Labourer",
        "Labourer Agricultural": "Agricultural Labourer",
        "Labourer, General": "General Labourer",
        "Labourer, Agricultural": "Agricultural Labourer",
        "Agricultural Labourer General": "General Agricultural Labourer",
        "Clerk Bank": "Bank Clerk",
        "Clerk Railway": "Railway Clerk",
        "Clerk Post Office": "Post Office Clerk",
        "Porter Railway": "Railway Porter",
        "Labourer Dock": "Dock Labourer",
        "Labourer Road": "Road Labourer",
        "Labourer Railway": "Railway Labourer",
        "Labourer Farm": "Farm Labourer",
        
        // Common spelling corrections
        "Sempstress": "Seamstress",
        "Seamstres": "Seamstress",
        "Seamtress": "Seamstress",
        "Seamsteress": "Seamstress",
        "Seamestress": "Seamstress",
        "Seamsterss": "Seamstress",
        "Seamistress": "Seamstress",
        "Semstress": "Seamstress",
        
        // Scholar variants
        "Scholars": "Scholar",
        "Schollar": "Scholar",
        "Scolar": "Scholar",
        "Scholoar": "Scholar",
        "Scholors": "Scholar",
        "Schollars": "Scholar",
        "Schoolar": "Scholar",
        "Scohlar": "Scholar",
        "Scoller": "Scholar",
        "Scollor": "Scholar",
        "Scollar": "Scholar",
        "Scholor": "Scholar",
        "Scholler": "Scholar",
        "Schol": "Scholar",
        "Sholars": "Scholar",
        "Shollar": "Scholar",
        "Sholar": "Scholar",
        
        // Labourer variants
        "Labourers": "Labourer",
        "Laborour": "Labourer",
        "Labrour": "Labourer",
        "Laboror": "Labourer",
        "Laberour": "Labourer",
        "Labouer": "Labourer",
        "Labour": "Labourer",
        "Labours": "Labourer",
        "Labiour": "Labourer",
        "Labouring": "Labourer",
        
        // Comprehensive abbreviations
        "Agl Labourer": "Agricultural Labourer",
        "Agrl Labourer": "Agricultural Labourer",
        "Agr Labourer": "Agricultural Labourer",
        "Agr. Labourer": "Agricultural Labourer",
        "Agrl. Labourer": "Agricultural Labourer",
        "Agl. Labourer": "Agricultural Labourer",
        "Agricl Labourer": "Agricultural Labourer",
        "Agric Labourer": "Agricultural Labourer",
        "Agri Labourer": "Agricultural Labourer",
        "Ag Labourer": "Agricultural Labourer",
        "Ag. Labourer": "Agricultural Labourer",
        "A Labourer": "Agricultural Labourer",
        "Agriculture Labourer": "Agricultural Labourer",
        "Agricultural Labour": "Agricultural Labourer",
        "Agricultural Labor": "Agricultural Labourer",
        "Agricultural Lab": "Agricultural Labourer",
        "Agricultural Labr": "Agricultural Labourer",
        "Agricultural Labrour": "Agricultural Labourer",
        "Agricultural Laberour": "Agricultural Labourer",
        "Agricultural Laboue": "Agricultural Labourer",
        "Agricultural Labouer": "Agricultural Labourer",
        "Agricultral Labourer": "Agricultural Labourer",
        "Agriculural Labourer": "Agricultural Labourer",
        "Agricutural Labourer": "Agricultural Labourer",
        "Agricult Labourer": "Agricultural Labourer",
        "Agricul Labourer": "Agricultural Labourer",
        "Agricultl Labourer": "Agricultural Labourer",
        
        "Genl Labourer": "General Labourer",
        "Gen Labourer": "General Labourer",
        "G Labourer": "General Labourer",
        "Gl Labourer": "General Labourer",
        "General Laberour": "General Labourer",
        "General Labrour": "General Labourer",
        "General Laborour": "General Labourer",
        "Genral Labourer": "General Labourer",
        
        "N S Teacher": "National School Teacher",
        "N.S. Teacher": "National School Teacher",
        "NS Teacher": "National School Teacher",
        "Nat Teacher": "National Teacher",
        "Natl Teacher": "National Teacher",
        "National S Teacher": "National School Teacher",
        "Nat School Teacher": "National School Teacher",
        "Natl School Teacher": "National School Teacher",
        "N School Teacher": "National School Teacher",
        
        // Religious
        "R C Priest": "Roman Catholic Priest",
        "R.C. Priest": "Roman Catholic Priest",
        "RC Priest": "Roman Catholic Priest",
        "R C Clergyman": "Roman Catholic Clergyman",
        "R.C. Clergyman": "Roman Catholic Clergyman",
        "RC Clergyman": "Roman Catholic Clergyman",
        
        // Other corrections
        "Coalminer": "Coal Miner",
        "Millworker": "Mill Worker",
        "Dressmaking": "Dressmaker",
        "House keeper": "Housekeeper",
        "Hous Keeper": "Housekeeper",
        "HouseKeeper": "Housekeeper",
        "Housekeper": "Housekeeper",
        "Houskeeper": "Housekeeper",
        
        // Carpenter variants
        "Carpinter": "Carpenter",
        "Carpanter": "Carpenter",
        "Carpentar": "Carpenter",
        "Cartpenter": "Carpenter",
        "Corpenter": "Carpenter",
        "Carpender": "Carpenter"
    };
    
    // Apply direct corrections
    if (corrections[corrected]) {
        corrected = corrections[corrected];
    }
    
    return corrected;
}

// Process EXACTLY batch 2: records 301-600 (300 records)
const batch2Data = parsedData.data.slice(300, 600);
console.log(`Processing batch 2: records 301-600 (exactly ${batch2Data.length} records)`);

const processedBatch2 = batch2Data.map(row => ({
occupation: row.occupation,
count: row.count,
corrected_occupation: correctOccupation(row.occupation)
}));

// Convert to CSV
const batch2CSV = Papa.unparse(processedBatch2);

console.log("Sample of combined improvements:");
for (let i = 0; i < 20; i++) {
const row = processedBatch2[i];
if (row.occupation !== row.corrected_occupation) {
console.log(`${300+i+1}. "${row.occupation}" → "${row.corrected_occupation}" ✓`);
} else {
console.log(`${300+i+1}. "${row.occupation}" (no change)`);
}
}

console.log("\n" + "=".repeat(80));
console.log("COMBINED SCRIPT BATCH 2 CSV OUTPUT:");
console.log("=".repeat(80));
console.log(batch2CSV);