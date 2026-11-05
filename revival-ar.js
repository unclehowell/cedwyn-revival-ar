/* Revival AR v0.2.4 — Llandough. Photo tripods from photos.json (tap a tripod -> the photograph taken from there). Positions and evidence from SITES.json; tour from tour.json. — Sion's Tab agent */
(function(){
'use strict';
// opening camera per site (3D model loop, issue #198): Tŷ Mawr opens on the house group, not the whole 180 m model
var CAM={tymawr:{target:'-10m 2m 2m',orbit:'-30deg 65deg 120m',fov:'30deg'}};
var COL={roundhouse:'#b5874a',villa:'#c4553a',monastery:'#5f8fb8',tymawr:'#e8e2cf'};
var UI={en:{conf:'Confidence',known:'From the record',est:'Reconstruction — estimated',src:'Sources',view:'View 3D / AR',tour:'Tour stop',away:'away',here:'You are here',off:'Location off — tap to show distances.',deny:'Location not shared; distances hidden.',onsite:'You are at this site. Tap “View in your space”, point the phone at open ground, turn until the arrow points north, then place it.',far:'You are {d} from this site. AR works anywhere at true size; on site it stands where the record puts it.',go:'Show on map',stop:'Stop',photo:'Photo',swipe:'swipe for more',tripod:'Tripod position estimated by matching the photograph to the model.'},
 cy:{conf:'Hyder',known:"O'r cofnod",est:'Ail-greadigaeth — amcangyfrif',src:'Ffynonellau',view:'Gweld 3D / AR',tour:'Man aros',away:'i ffwrdd',here:'Rydych chi yma',off:'Lleoliad i ffwrdd — tapiwch i weld pellteroedd.',deny:'Lleoliad heb ei rannu.',onsite:"Rydych chi ar y safle. Tapiwch “View in your space”, trowch nes bod y saeth yn pwyntio i'r gogledd, yna gosodwch.",far:'Rydych {d} o’r safle.',go:'Dangos ar y map',stop:'Man aros',photo:'Llun',swipe:'llithro am ragor',tripod:'Safle’r trybedd wedi’i amcangyfrif drwy gymharu’r llun â’r model.'},
 es:{conf:'Confianza',known:'Del registro',est:'Reconstrucción — estimada',src:'Fuentes',view:'Ver 3D / RA',tour:'Parada',away:'de distancia',here:'Usted está aquí',off:'Ubicación desactivada — toque para ver distancias.',deny:'Ubicación no compartida.',onsite:'Está en el sitio. Toque “View in your space”, gire hasta que la flecha apunte al norte y colóquelo.',far:'Está a {d} del sitio.',go:'Ver en el mapa',stop:'Parada',photo:'Foto',swipe:'deslice para ver más',tripod:'Posición del trípode estimada comparando la foto con el modelo.'}};
var lang=(navigator.language||'en').slice(0,2); if(!UI[lang]) lang='en';
var S=null,T=null,P={tripods:[]},map=null,me=null,meMk=null,meAcc=null,cur='villa',heading=null,markers={};
function $(id){return document.getElementById(id)}
function t(k){return UI[lang][k]||UI.en[k]}
function nm(s){return (s.name&&(s.name[lang]||s.name.en))||s.id}
function esc(x){return String(x).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function hav(a,b){var R=6371000,r=Math.PI/180,dl=(b.lat-a.lat)*r,dn=(b.lon-a.lon)*r,x=Math.sin(dl/2)*Math.sin(dl/2)+Math.cos(a.lat*r)*Math.cos(b.lat*r)*Math.sin(dn/2)*Math.sin(dn/2);return 2*R*Math.asin(Math.sqrt(x))}
function brg(a,b){var r=Math.PI/180,y=Math.sin((b.lon-a.lon)*r)*Math.cos(b.lat*r),x=Math.cos(a.lat*r)*Math.sin(b.lat*r)-Math.sin(a.lat*r)*Math.cos(b.lat*r)*Math.cos((b.lon-a.lon)*r);return (Math.atan2(y,x)/r+360)%360}
function fmt(m){return m<1000?Math.round(m)+' m':(m/1000).toFixed(m<10000?1:0)+' km'}
function card(s){
  var d=me?'<span class="dist">'+fmt(hav(me,s))+' '+t('away')+' · '+['N','NE','E','SE','S','SW','W','NW'][Math.round(brg(me,s)/45)%8]+'</span><br>':'';
  return '<li><span class="dot" style="background:'+COL[s.id]+'"></span><div><h3>'+esc(nm(s))+'</h3><div class="meta">'+d+esc(s.period)+'</div>'+
   '<div class="btns"><button class="go" data-view="'+s.id+'">'+t('view')+'</button><button data-tour="'+s.id+'">'+t('tour')+'</button></div></div></li>'}
function renderCards(){var h='';S.sites.forEach(function(s){h+=card(s)});$('cards').innerHTML=h;
  [].forEach.call(document.querySelectorAll('[data-view]'),function(b){b.onclick=function(){show(b.getAttribute('data-view'))}});
  [].forEach.call(document.querySelectorAll('[data-tour]'),function(b){b.onclick=function(){tab('tour');var el=document.querySelector('.stops li[data-pin="'+b.getAttribute('data-tour')+'"]');if(el)el.scrollIntoView({behavior:'smooth'})}})}
function tab(n){[].forEach.call(document.querySelectorAll('.tabs button'),function(b){b.classList.toggle('on',b.getAttribute('data-tab')===n)});
  [].forEach.call(document.querySelectorAll('.pane'),function(p){p.classList.toggle('on',p.id==='tab-'+n)}); if(n==='map'&&map) setTimeout(function(){map.invalidateSize()},50)}
function show(id){cur=id;var s=S.sites.filter(function(x){return x.id===id})[0];tab('view');
  [].forEach.call($('pick').children,function(b){b.classList.toggle('on',b.getAttribute('data-id')===id)});
  var mv=$('mv'); mv.setAttribute('src',s.model); mv.setAttribute('alt',nm(s)+' — reconstruction'); mv.setAttribute('ios-src','');
  var c=CAM[id]; if(c){mv.setAttribute('min-camera-orbit','auto auto 20m');mv.setAttribute('max-camera-orbit','auto auto 400m');mv.setAttribute('camera-target',c.target);mv.setAttribute('field-of-view',c.fov);mv.setAttribute('camera-orbit',c.orbit);}else{['min-camera-orbit','max-camera-orbit','camera-target','field-of-view'].forEach(function(a){mv.removeAttribute(a)});mv.setAttribute('camera-orbit','35deg 62deg auto');}
  if(mv.jumpCameraToGoal)mv.jumpCameraToGoal();
  tripods(id);
  var L='<h3>'+esc(nm(s))+'</h3><div class="meta">'+esc(s.period)+'</div><p><b>'+t('conf')+':</b> '+esc(s.confidence)+'</p>';
  L+='<p><span class="tag k">'+t('known')+'</span></p><ul>'+s.known.map(function(k){return '<li>'+esc(k)+'</li>'}).join('')+'</ul>';
  L+='<p><span class="tag e">'+t('est')+'</span></p><ul>'+s.estimated.map(function(k){return '<li>'+esc(k)+'</li>'}).join('')+'</ul>';
  L+='<p><b>'+t('src')+'</b></p><ul>'+s.evidence.map(function(e){return '<li>'+(e.url?'<a href="'+esc(e.url)+'" target="_blank" rel="noopener">'+esc(e.label)+'</a>':esc(e.label))+'</li>'}).join('')+'</ul>';
  L+='<p class="meta">'+s.lat.toFixed(6)+', '+s.lon.toFixed(6)+'</p>';
  $('detail').innerHTML=L; onsite()}
function tripods(id){var mv=$('mv');[].forEach.call(mv.querySelectorAll('.tripod'),function(e){e.remove()});
  (P.tripods||[]).filter(function(p){return p.site===id}).forEach(function(p,i){var b=document.createElement('button');b.className='tripod';b.slot='hotspot-photo-'+i;
    b.setAttribute('data-position',p.x+'m 1.7m '+p.z+'m');b.setAttribute('data-normal','0m 1m 0m');b.setAttribute('aria-label',t('photo')+': '+p.photos[0].caption);
    b.innerHTML='<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M4 7h3l1.5-2h7L17 7h3a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1z" fill="#16201b"/><circle cx="12" cy="12.5" r="3.6" fill="#e6c77f"/></svg>';
    b.onclick=function(e){e.stopPropagation();photo(p)}; mv.appendChild(b)})}
function photo(p){var d=$('photo'),h='';p.photos.forEach(function(f,i){h+='<figure><img src="'+esc(f.src)+'" alt="'+esc(f.view||f.caption)+'" loading="lazy"><figcaption><b>'+esc(f.caption)+'</b>'+(f.view?'<br>'+esc(f.view):'')+
    (p.photos.length>1?'<br><span class="small">'+(i+1)+' / '+p.photos.length+' · '+t('swipe')+'</span>':'')+'</figcaption></figure>'});
  $('photoset').innerHTML=h; $('photonote').textContent=p.estimated?t('tripod'):''; if(d.showModal)d.showModal();else d.setAttribute('open','')}
function onsite(){var s=S.sites.filter(function(x){return x.id===cur})[0];if(!s)return;var h='';
  if(me){var d=hav(me,s); h='<p><span class="compass" id="cmp">↑</span> '+(d<80?t('onsite'):t('far').replace('{d}',fmt(d)))+'</p>'}
  $('onsite').innerHTML=h; spin()}
function spin(){var c=$('cmp'); if(c&&heading!=null) c.style.transform='rotate('+(-heading)+'deg)'}
function initMap(){
  map=L.map('map',{zoomControl:true,attributionControl:true}).setView([51.4522,-3.1989],17);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);
  var b=[];S.sites.forEach(function(s){var m=L.circleMarker([s.lat,s.lon],{radius:10,color:'#111',weight:2,fillColor:COL[s.id],fillOpacity:.95}).addTo(map);
    m.bindTooltip(nm(s),{permanent:true,direction:(s.id==='roundhouse'?'left':'right'),className:'lbl',offset:[(s.id==='roundhouse'?-8:8),0]}); m.on('click',function(){show(s.id)}); markers[s.id]=m; b.push([s.lat,s.lon])});
  var c=S.sites.filter(function(x){return x.id==='monastery'})[0].cross;
  if(c){L.circleMarker([c.lat,c.lon],{radius:5,color:'#5f8fb8',weight:2,fillColor:'#fff',fillOpacity:1}).addTo(map).bindTooltip('Pillar cross, '+c.height_m+' m')}
  map.fitBounds(b,{padding:[40,40],maxZoom:18})}
function locate(){
  if(!navigator.geolocation){$('gpsline').textContent=t('deny');return}
  navigator.geolocation.watchPosition(function(p){me={lat:p.coords.latitude,lon:p.coords.longitude};
    var ll=[me.lat,me.lon];
    if(!meMk){meMk=L.circleMarker(ll,{radius:8,color:'#fff',weight:3,fillColor:'#2a7fff',fillOpacity:1}).addTo(map).bindTooltip(t('here'));meAcc=L.circle(ll,{radius:p.coords.accuracy,color:'#2a7fff',weight:1,fillOpacity:.08}).addTo(map)}
    else{meMk.setLatLng(ll);meAcc.setLatLng(ll).setRadius(p.coords.accuracy)}
    var near=S.sites.map(function(s){return [hav(me,s),s]}).sort(function(a,b){return a[0]-b[0]})[0];
    $('gpsline').textContent=t('here')+' (±'+Math.round(p.coords.accuracy)+' m) · '+nm(near[1])+' '+fmt(near[0]);
    renderCards(); onsite()},function(){$('gpsline').textContent=t('deny')},{enableHighAccuracy:true,maximumAge:5000,timeout:20000});
  var h=function(e){var v=e.webkitCompassHeading!=null?e.webkitCompassHeading:(e.absolute&&e.alpha!=null?360-e.alpha:null);if(v!=null){heading=v;spin()}};
  try{if(window.DeviceOrientationEvent&&typeof DeviceOrientationEvent.requestPermission==='function'){DeviceOrientationEvent.requestPermission().then(function(r){if(r==='granted')window.addEventListener('deviceorientation',h)}).catch(function(){})}
  else{window.addEventListener('deviceorientationabsolute',h);window.addEventListener('deviceorientation',h)}}catch(e){}}
function renderTour(){var h='';T.stops.forEach(function(s){var site=S.sites.filter(function(x){return x.id===s.pin})[0];
  h+='<li data-pin="'+s.pin+'"><h3>'+esc(s.title[lang]||s.title.en)+'</h3><div class="d">'+esc(s.date)+' · '+esc(nm(site))+'</div><p>'+esc(s[lang]||s.en)+'</p><div class="src">'+t('src')+': '+esc(s.sources.join('; '))+'</div>'+
   '<button data-show="'+s.pin+'">'+t('view')+'</button> <button data-map="'+s.pin+'">'+t('go')+'</button></li>'});
  $('stops').innerHTML=h;
  [].forEach.call(document.querySelectorAll('[data-show]'),function(b){b.onclick=function(){show(b.getAttribute('data-show'))}});
  [].forEach.call(document.querySelectorAll('[data-map]'),function(b){b.onclick=function(){var s=S.sites.filter(function(x){return x.id===b.getAttribute('data-map')})[0];tab('map');map.setView([s.lat,s.lon],18);markers[s.id].openTooltip()}})}
function pick(){var h='';S.sites.forEach(function(s){h+='<button data-id="'+s.id+'">'+esc(nm(s))+'</button>'});$('pick').innerHTML=h;
  [].forEach.call($('pick').children,function(b){b.onclick=function(){show(b.getAttribute('data-id'))}})}
function all(){renderCards();renderTour();pick();show(cur);var q=location.hash.replace('#','');tab(['map','view','tour'].indexOf(q)>=0?q:'map')}
[].forEach.call(document.querySelectorAll('.tabs button'),function(b){b.onclick=function(){tab(b.getAttribute('data-tab'))}});
$('lang').value=lang; $('lang').onchange=function(){lang=this.value;document.documentElement.lang=lang;if(!me)$('gpsline').textContent=t('off');all();Object.keys(markers).forEach(function(k){var s=S.sites.filter(function(x){return x.id===k})[0];markers[k].setTooltipContent(nm(s))})};
$('info').onclick=function(){var d=$('about');if(d.showModal)d.showModal();else d.setAttribute('open','')};
$('locate').onclick=locate;
Promise.all([fetch('SITES.json').then(function(r){return r.json()}),fetch('tour.json').then(function(r){return r.json()}),fetch('photos.json?v=0.2.4').then(function(r){return r.json()}).catch(function(){return {tripods:[]}})]).then(function(a){S=a[0];T=a[1];P=a[2]||P;
  var p=new URLSearchParams(location.search).get('site'); if(p) cur=p;
  initMap(); all(); if(p) show(p);});
})();
