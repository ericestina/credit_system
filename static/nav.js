(function(){
  // marca ativo pela URL atual
  const path = (location.pathname || '/').replace(/\/+$/,'') || '/';
  const map = { '/':'home', '/policy':'policy', '/apply':'apply', '/model':'model' };
  const current = map[path];
  if (current){
    const el = document.querySelector(`.navlinks a[data-nav="${current}"]`);
    if (el && !el.classList.contains('nav-cta')) el.classList.add('active');
  }

  // menu mobile
  const btn = document.querySelector('.nav-toggle');
  const nav = document.getElementById('main-nav');
  if (btn && nav){
    btn.addEventListener('click', ()=>{
      const open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
    });
  }
})();

(function(){
  const path = (location.pathname || '/').replace(/\/+$/,'') || '/';
  const map  = { '/':'home', '/policy':'policy', '/apply':'apply', '/model':'model' };
  const current = map[path];
  if(current){
    const a = document.querySelector(`.navlinks a[data-nav="${current}"]`);
    if(a && !a.classList.contains('nav-cta')) a.classList.add('active');
  }
})();