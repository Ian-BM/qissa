/* Build-only dependencies: potrace, jimp (potrace dependency), @resvg/resvg-js.
   Run from the repo root with those modules installed in NODE_PATH. */
const fs = require('fs');
const path = require('path');
const potrace = require('potrace');
const Jimp = require('jimp');
const { Resvg } = require('@resvg/resvg-js');
const output = path.resolve('static/branding');
const render = (svg, width) => new Resvg(svg, {fitTo:{mode:'width',value:width}}).render().asPng();
function bounds(image, predicate) {
  const {data,width,height} = image.bitmap;
  let left=width, top=height, right=-1, bottom=-1;
  for (let y=0;y<height;y++) for (let x=0;x<width;x++) {
    const i=(y*width+x)*4;
    if (predicate(data,i)) {left=Math.min(left,x);top=Math.min(top,y);right=Math.max(right,x);bottom=Math.max(bottom,y);}
  }
  if(right<left)throw Error('Empty artwork');
  return {left,top,width:right-left+1,height:bottom-top+1};
}
(async()=>{
  fs.mkdirSync(output,{recursive:true});
  const qFile=path.resolve('design/branding/approved-q.jpg');
  const source=await Jimp.read(qFile);
  const box=bounds(source,(pixels,i)=>pixels[i]<128 && pixels[i+1]<128 && pixels[i+2]<128);
  const traced=await new Promise((resolve,reject)=>potrace.trace(qFile,{threshold:128,turdSize:4,optTolerance:0.1,color:'#20252C'},(err,svg)=>err?reject(err):resolve(svg)));
  const shape=traced.match(/<path[^>]*d="([^"]+)"/)[1];
  const scale=424/Math.max(box.width,box.height);
  const x=(512-box.width*scale)/2-box.left*scale;
  const y=(512-box.height*scale)/2-box.top*scale;
  const glyph=color=>`<path fill-rule="evenodd" fill="${color}" d="${shape}" transform="translate(${x.toFixed(4)} ${y.toFixed(4)}) scale(${scale.toFixed(6)})"/>`;
  const wrap=(inside,label)=>`<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="${label}">${inside}</svg>\n`;
  const mark=wrap(glyph('#20252C'),'Qissa Q mark');
  const favicon=wrap('<rect width="512" height="512" rx="80" fill="#111419"/>'+glyph('#F4F0E8'),'Qissa');
  fs.writeFileSync(path.join(output,'qissa-mark.svg'),mark);
  fs.writeFileSync(path.join(output,'favicon.svg'),favicon);
  fs.writeFileSync('static/favicon.svg',favicon); // Compatible alias; old generic artwork removed.
  const sizes=[16,32,48,180,192,512],images=new Map();
  for(const size of sizes)images.set(size,render(favicon,size));
  for(const size of [16,32])fs.writeFileSync(path.join(output,`favicon-${size}x${size}.png`),images.get(size));
  fs.writeFileSync(path.join(output,'apple-touch-icon.png'),images.get(180));
  for(const size of [192,512])fs.writeFileSync(path.join(output,`android-chrome-${size}x${size}.png`),images.get(size));
  const iconSizes=[16,32,48];
  const header=Buffer.alloc(6+16*iconSizes.length);
  header.writeUInt16LE(1,2);header.writeUInt16LE(iconSizes.length,4);
  let offset=header.length;
  iconSizes.forEach((size,index)=>{
    const at=6+16*index,png=images.get(size);
    header[at]=size;header[at+1]=size;header.writeUInt16LE(1,at+4);header.writeUInt16LE(32,at+6);
    header.writeUInt32LE(png.length,at+8);header.writeUInt32LE(offset,at+12);offset+=png.length;
  });
  fs.writeFileSync(path.join(output,'favicon.ico'),Buffer.concat([header,...iconSizes.map(size=>images.get(size))]));
  const logoFile=path.resolve('design/branding/approved-wordmark.png');
  const logo=await Jimp.read(logoFile);
  const cropped=bounds(logo,(pixels,i)=>pixels[i]<128 && pixels[i+1]<128 && pixels[i+2]<128);
  const padding=6,width=cropped.width+padding*2,height=cropped.height+padding*2;
  const logoTrace=await new Promise((resolve,reject)=>potrace.trace(logoFile,{threshold:128,turdSize:4,optTolerance:0.1,color:'#20252C'},(err,svg)=>err?reject(err):resolve(svg)));
  const logoShape=logoTrace.match(/<path[^>]*d="([^"]+)"/)[1];
  for(const [name,color] of [['qissa-logo.png','#20252C'],['qissa-logo-ivory.png','#F4F0E8']]){
    // Render a single trace of the approved artwork in two inks. No font substitution.
    const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}"><path fill-rule="evenodd" fill="${color}" d="${logoShape}" transform="translate(${padding-cropped.left} ${padding-cropped.top})"/></svg>`;
    fs.writeFileSync(path.join(output,name),render(svg,480));
  }
  fs.writeFileSync(path.join(output,'site.webmanifest'),JSON.stringify({name:'Qissa',short_name:'Qissa',lang:'sw',start_url:'/',scope:'/',display:'standalone',background_color:'#111419',theme_color:'#111419',icons:[192,512].map(size=>({src:`/static/branding/android-chrome-${size}x${size}.png?v=logo1`,sizes:`${size}x${size}`,type:'image/png',purpose:'any'}))},null,2)+'\n');
  console.log(JSON.stringify({qBounds:box,logoBounds:cropped,logoOutputWidth:480,files:fs.readdirSync(output)},null,2));
})().catch(error=>{console.error(error);process.exit(1)});
