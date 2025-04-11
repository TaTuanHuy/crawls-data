const fs = require('fs');
const path = require('path');

// const bonTamPath =  path.join(__dirname, 'bon-tam/bon-tam.json');
// const bonCauPath =  path.join(__dirname, 'boncau/boncau.json');
// const chauRuaPath =  path.join(__dirname, 'chau-rua/chau-rua.json');
// const napBonCauPath =  path.join(__dirname, 'nap-bon-cau/nap-bon-cau.json');
// const phuKienNhaTamPath =  path.join(__dirname, 'phu-kien-nha-tam/phu-kien-nha-tam.json');
// const senTamPath =  path.join(__dirname, 'sen-tam/sen-tam.json');
// const tbvsccPath =  path.join(__dirname, 'thiet-bi-ve-sinh-khu-cong/thiet-bi-ve-sinh-khu-cong.json');
// const voiPath =  path.join(__dirname, 'voi/voi.json');

// const arrPath = [
//     bonTamPath,
//     bonCauPath,
//     chauRuaPath,
//     napBonCauPath,
//     phuKienNhaTamPath,
//     senTamPath,
//     tbvsccPath,
//     voiPath,
// ]

// function readJsonArray(filePath) {
//     if (!fs.existsSync(filePath)) return []; // Nếu file chưa tồn tại
//     const content = fs.readFileSync(filePath, 'utf8');
//     return content.trim() ? JSON.parse(content) : [];
//   }

// // // MAP DATA TO RESULT JSON FILE
// const resultPath = path.join(__dirname, 'result.json');
// for(let path of arrPath){
//     try {
//         const sourceData = readJsonArray(path); // Dữ liệu mới cần thêm vào
//         const resultData = readJsonArray(resultPath); // Dữ liệu đã có
        
//         // Gộp dữ liệu cũ và mới
//         const combinedData = [...resultData, ...sourceData];
        
//         // Ghi lại vào file result.json
//         fs.writeFileSync(resultPath, JSON.stringify(combinedData, null, 2), 'utf8');
//         console.log('✅ Đã thêm dữ liệu mới vào result.json mà không mất dữ liệu cũ!');
//     } catch (err) {
//         console.error('❌ Lỗi xử lý JSON:', err);
//     }
// }


//  READ RESULT FILE

function convertSkuArray(data) {
}

function convertData(data) {
  const result = data.reduce((pre, item) => {
    const convertObj = {
      companyName: toto,
      tag: '',
      display: true,
      attribute: [
        {
          title: 'title', value: 'Default title',
        }
      ],

      weight: 0,
      manager: 'haravan',
      order: 'continue'
    }

    if(item?.name){
      const {name}= item
      convertObj.url =  name.split(' ').join('-').toLowerCase()
      convertObj.name = name
    } 
    if(item?.sku){
      convertObj.code = data.code
    } 
    if(item?.price){
      convertObj.price = data.price
    } 

    return [...pre, convertObj]
  },[])
}



const resultPath = path.join(__dirname, 'result.json');

fs.readFile(resultPath, 'utf8', (err, data) => {
    if (err) {
      console.error('Không thể đọc file nguồn:', err);
      return;
    }
  
    try {
      const originalData = JSON.parse(data);
      const newJsonData = convertData(originalData);
      // const convertData = convertSkuArray(originalData)
      //   console.log(convertData);


      //   fs.writeFileSync(resultPath, JSON.stringify(convertData, null, 2), 'utf8');
      //   console.log('✅ convert sku array!');
        
     
    } catch (parseErr) {
      console.error('Lỗi khi parse JSON:', parseErr);
    }
  });