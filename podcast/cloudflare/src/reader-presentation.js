// Presentation only: known enum and bounded numeric values, never arbitrary CSS.
export function readerPresentation(html, params) {
 const mode=params.get('mode')==='reader'?'reader':'original';
 const theme=['light','sepia','dark'].includes(params.get('theme'))?params.get('theme'):'original';
 const value=Number(params.get('scale')||100);
 const scale=Number.isFinite(value)?Math.min(180,Math.max(80,Math.round(value))):100;
 const n=v=>(v*scale/100).toFixed(2)+'px';
 const palettes={light:['#fafafa','#20242c','#424955','#745514','#e9e9ec'],sepia:['#f4ead7','#372d20','#5c4d39','#735318','#e3d7bd'],dark:['#15171c','#f0eee7','#c3c4cb','#e6c36a','#292c35']};
 let css='';
 if(theme!=='original'){
  const [bg,fg,muted,accent,panel]=palettes[theme];
  css+='body{background:'+bg+'!important;color:'+fg+'!important}.headline,.sec-title,.title,.puzzle-title,.puzzle-q,.fun-text,.txt,.answer{color:'+fg+'!important}.summary,.source,.metrics,.original-note,.puzzle-how,.sub,.spec-label{color:'+muted+'!important}.source a,.tab,.fun-tag{color:'+accent+'!important}.spec-cell,.bias-note,.fun-box,.puzzle-box,.wpuzzle-box,.answer{background:'+panel+'!important;border-color:'+muted+'!important}.item{border-color:'+panel+'!important}';
 }
 if(scale!==100||mode==='reader')css+='.headline{font-size:'+n(mode==='reader'?20:16)+'!important}.summary,.txt,.puzzle-how,.puzzle-q,.answer,.fun-text{font-size:'+n(mode==='reader'?18:14)+'!important;line-height:1.75!important}.source,.metrics,.bias-note,.original-note{font-size:'+n(12)+'!important}.sec-title{font-size:'+n(24)+'!important}.puzzle-title{font-size:'+n(22)+'!important}.tab{font-size:'+n(13)+'!important}';
 if(mode==='reader')css+='.wrap{max-width:760px;padding:28px 22px 64px}.tabs,.section-radio{display:none!important}.sec{display:block!important;animation:none!important;margin-top:38px}.sec+.sec{border-top:1px solid #8886;padding-top:30px}.item{padding:22px 0}.summary{max-width:65ch}.spectrum{grid-template-columns:1fr!important}.spec-cell{padding:14px}.title{font-size:36px!important}.original-note{display:none}';
 css+='@media(max-width:600px){.wrap{padding-left:16px;padding-right:16px}.spectrum{grid-template-columns:1fr}.headline,.summary,.txt,.answer,.puzzle-q,.fun-text{overflow-wrap:anywhere}}';
 return html.replace('</head>','<style id="reader-presentation">'+css+'</style></head>');
}
