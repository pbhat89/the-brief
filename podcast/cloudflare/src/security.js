export const TTL = 7 * 86400;
export const MAX = 8 * 1024 * 1024;
export const hex = b => Array.from(new Uint8Array(b), v => v.toString(16).padStart(2,'0')).join('');
export const digest = async s => hex(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)));
export function equal(a,b) { if(typeof a !== 'string'||typeof b !== 'string'||a.length!==b.length)return false; let n=0;for(let i=0;i<a.length;i++)n|=a.charCodeAt(i)^b.charCodeAt(i);return n===0; }
export async function pinHash(pin,salt) {
 const k=await crypto.subtle.importKey('raw',new TextEncoder().encode(pin),'PBKDF2',false,['deriveBits']);
 return hex(await crypto.subtle.deriveBits({name:'PBKDF2',hash:'SHA-256',salt:new TextEncoder().encode(salt),iterations:100000},k,256));
}
export function range(header,size) {
 if(!header)return [0,size-1];
 const m=/^bytes=(\d*)-(\d*)$/.exec(header);if(!m||(!m[1]&&!m[2]))return null;
 let a=m[1]?Number(m[1]):Math.max(0,size-Number(m[2]));let b=m[1]?(m[2]?Math.min(Number(m[2]),size-1):size-1):size-1;
 return Number.isSafeInteger(a)&&Number.isSafeInteger(b)&&a>=0&&a<=b&&a<size?[a,b]:null;
}
// Require two consecutive MPEG-1/2 Layer III frames; arbitrary ID3 or magic bytes are insufficient.
export function mp3(bytes) {
 let start=0;
 if(bytes[0]===73&&bytes[1]===68&&bytes[2]===51){if(bytes.length<10||bytes.slice(6,10).some(x=>x>127))return false;start=10+(bytes[6]<<21)+(bytes[7]<<14)+(bytes[8]<<7)+bytes[9];}
 function frame(i){const b=bytes;if(b[i]!==255||(b[i+1]&224)!==224)return 0;const v=(b[i+1]>>3)&3,l=(b[i+1]>>1)&3,br=b[i+2]>>4,sr=(b[i+2]>>2)&3;if(v===1||l!==1||br===0||br===15||sr===3)return 0;const rates=v===3?[0,32,40,48,56,64,80,96,112,128,160,192,224,256,320]:[0,8,16,24,32,40,48,56,64,80,96,112,128,144,160];const hz=[44100,48000,32000][sr]/(v===3?1:v===2?2:4);return Math.floor((v===3?144000:72000)*rates[br]/hz)+((b[i+2]>>1)&1);}
 const n=frame(start);return n>0&&start+n+4<=bytes.length&&frame(start+n)>0;
}
