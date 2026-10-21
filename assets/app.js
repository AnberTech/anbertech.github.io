(function(){
  var r=document.documentElement,b=document.getElementById('theme');
  if(b)b.addEventListener('click',function(){
    var n=r.getAttribute('data-theme')==='light'?'dark':'light';
    r.setAttribute('data-theme',n);
    try{localStorage.setItem('ab_theme',n)}catch(e){}
  });
  [].forEach.call(document.querySelectorAll('.card'),function(c){
    c.addEventListener('pointermove',function(e){
      var k=c.getBoundingClientRect();
      c.style.setProperty('--mx',(e.clientX-k.left)+'px');
      c.style.setProperty('--my',(e.clientY-k.top)+'px');
    });
  });
})();
(function(){
  /* dil menüsü: dışarı tıklayınca veya Esc ile kapanır */
  var lm=document.querySelector('.lang-menu');if(!lm)return;
  document.addEventListener('click',function(e){if(lm.open&&!lm.contains(e.target))lm.open=false});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&lm.open){lm.open=false;lm.querySelector('summary').focus()}});
})();
