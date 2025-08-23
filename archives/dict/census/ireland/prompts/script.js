// Combined script: Best spelling corrections + better bracket/whitespace handling
import Papa from 'papaparse';
const fileContent = await window.fs.readFile('ire_occupation_1901.csv', { encoding: 'utf8' });

const parsedData = Papa.parse(fileContent, {
    header: true,
    skipEmptyLines: true,
    delimitersToGuess: [',', '\t', '|', ';']
});

// COMPREHENSIVE correction function
function correctOccupation(occupation) {
if (!occupation) return '';

    let corrected = occupation.trim();

    // ENHANCED PREPROCESSING
    // 1. Remove brackets first
    corrected = corrected.replace(/[\[\]()]/g, '');

    // 2. Handle hyphens as whitespace
    corrected = corrected.replace(/-/g, ' ');

    // 3. Condense duplicate whitespace
    corrected = corrected.replace(/\s+/g, ' ').trim();

    // COMPREHENSIVE CORRECTIONS (all previous ones PLUS missing ones)
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
        "Farmers Mother in Law": "Farmer's Mother in Law",
        "Accountants Clerk": "Accountant's Clerk",
        "Blacksmiths Apprentice": "Blacksmith's Apprentice",
        "Agricultural Labourers Daughter": "Agricultural Labourer's Daughter",
        "Fishermans Wife": "Fisherman's Wife",
        "Printers Labourer": "Printer's Labourer",
        "Chemists Apprentice": "Chemist's Apprentice",
        "Brewers Clerk": "Brewer's Clerk",
        "Shoemakers Wife": "Shoemaker's Wife",
        "Caretakers Wife": "Caretaker's Wife",
        "Blacksmiths Helper": "Blacksmith's Helper",
        "Childrens Nurse": "Children's Nurse",
        "Sailors Wife": "Sailor's Wife",
        "Shepherd Son": "Shepherd's Son",
        "Herd Daughter": "Herd's Daughter",
        "Tailors Daughter": "Tailor's Daughter",
        "Famers Daughter": "Farmer's Daughter",
        "Caretakers Daughter": "Caretaker's Daughter",
        "Farmeress Son": "Farmeress's Son",
        "Farmeress Daughter": "Farmeress's Daughter",
        "Labrs Wife": "Labourer's Wife",
        "Childrens Maid": "Children's Maid",

        // Combine compound words
        "House Keeper": "Housekeeper",
        "Boot Maker": "Bootmaker",
        "Shop Keeper": "Shopkeeper",
        "Watch Maker": "Watchmaker",
        "Gate Keeper": "Gatekeeper",
        "Time Keeper": "Timekeeper",
        "Care Taker": "Caretaker",
        "Clock Maker": "Clockmaker",
        "Cabinet Maker": "Cabinetmaker",
        "Cabnet Maker": "Cabinetmaker",
        "Shoe Maker": "Shoemaker",
        "Dress Maker": "Dressmaker",
        "Black Smith": "Blacksmith",
        "Paper Hanger": "Paperhanger",
        "Stone Mason": "Stonemason",
        "Gold Smith": "Goldsmith",
        "Tin Smith": "Tinsmith",
        "White Smith": "Whitesmith",
        "Mill Wright": "Millwright",
        "Ship Wright": "Shipwright",
        "Police Man": "Policeman",
        "Milk Man": "Milkman",
        "Bar Man": "Barman",
        "Bar Maid": "Barmaid",
        "Rope Maker": "Ropemaker",
        "Lace Maker": "Lacemaker",
        "Hair Dresser": "Hairdresser",
        "News Agent": "Newsagent",
        "Station Master": "Stationmaster",
        "Post Master": "Postmaster",
        "Post Mistress": "Postmistress",
        "Brick Layer": "Bricklayer",
        "Fisher Man": "Fisherman",
        "Iron Monger": "Ironmonger",
        "Post Man": "Postman",
        "House Maid": "Housemaid",
        "Silver Smith": "Silversmith",
        "Coach Man": "Coachman",
        "Wheel Wright": "Wheelwright",
        "Watch Man": "Watchman",
        "House Work": "Housework",
        "Book Keeper": "Bookkeeper",
        "Land Agents Assistant": "Land Agent's Assistant",
        "Hous Wife": "Housewife",
        "Farms Servant": "Farm Servant",
        "Paper Maker": "Papermaker",

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
        "General Servent": "General Servant",

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
        "Laborer General": "General Labourer",

        // Common spelling corrections
        "Sempstress": "Seamstress",
        "Seamstres": "Seamstress",
        "Seamtress": "Seamstress",
        "Seamsteress": "Seamstress",
        "Seamestress": "Seamstress",
        "Seamsterss": "Seamstress",
        "Seamistress": "Seamstress",
        "Semstress": "Seamstress",
        "Seanstress": "Seamstress",
        "Cleark": "Clerk",
        "Clarke": "Clerk",
        "Clerke": "Clerk",
        "Clerkess": "Clerk",
        "Plumer": "Plumber",
        "Shomaker": "Shoemaker",
        "Miliner": "Milliner",
        "Millner": "Milliner",
        "Laundres": "Laundress",
        "Aprentice": "Apprentice",
        "Serveant": "Servant",
        "At Chool": "At School",
        "Farm Serveant": "Farm Servant",
        "Farme Servant": "Farm Servant",
        "Buttler": "Butler",
        "Quay Labour": "Quay Labourer",
        "Shool Boy": "School Boy",
        "Frame Maker": "Framemaker",
        "Farm Laborour": "Farm Labourer",
        "Genl Labour": "Genl Labourer",
        "Grocers Manager": "Grocer's Manager",
        "Railway Labour": "Railway Labourer",

        "Scool Boy": "School Boy",
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
        "Sclolar": "Scholar",  // MISSING correction
        "Scoholar": "Scholar", // MISSING correction
        "Scholare": "Scholar", // MISSING correction
        "Scholour": "Scholar", // MISSING correction
        "Schlar": "Scholar", // MISSING
        "Schalor": "Scholar", // MISSING
        "Scholl": "Scholar", // MISSING
        "Shool": "Scholar", // MISSING
        "Scoolar": "Scholar",
        "Shoolar": "Scholar",

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
        "Labrourer": "Labourer",
        "Laburer": "Labourer",
        "Gen Laborer": "Gen Labourer",

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
        "Agricultur Labourer": "Agricultural Labourer", // MISSING

        "Genl Labourer": "General Labourer",
        "Gen Labourer": "General Labourer",
        "G Labourer": "General Labourer",
        "Gl Labourer": "General Labourer",
        "General Laberour": "General Labourer",
        "General Labrour": "General Labourer",
        "General Laborour": "General Labourer",
        "Genral Labourer": "General Labourer",
        "Genrl Labourer": "General Labourer", // MISSING

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
        "Huse Keeper": "Housekeeper", // MISSING

        // Carpenter variants
        "Carpinter": "Carpenter",
        "Carpanter": "Carpenter",
        "Carpentar": "Carpenter",
        "Cartpenter": "Carpenter",
        "Corpenter": "Carpenter",
        "Carpender": "Carpenter",

        // All other established corrections
        "Famers Son": "Farmer's Son",
        "Farmers' Son": "Farmer's Son", // Fix incorrect apostrophe
        "Market Gardner": "Market Gardener",
        "Gardner Domestic": "Gardener Domestic",
        "Plummer": "Plumber",
        "Salior": "Sailor",
        "Schloar": "Scholar",
        "At Shool": "At School",

        // Machinist
        "Machinest": "Machinist",
        "Machanist": "Machinist",
        "Machineist": "Machinist"
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