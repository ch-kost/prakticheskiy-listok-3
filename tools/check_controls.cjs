// Проверка встроенного JS Matplotlib без браузера и сторонних пакетов.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

for (let task = 1; task <= 5; task++) {
  const filename = path.join(__dirname, '..', 'animations', `3_${task}.html`);
  const html = fs.readFileSync(filename, 'utf8');
  assert(!/<(?:script|link)[^>]*(?:src|href)=["']https?:/i.test(html), 'Unexpected network dependency');
  assert(!/<i class="fa /.test(html), 'Unreplaced control icon');
  const elements = new Map();
  const document = new Proxy({
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, {src: '', value: 0, max: 0});
      return elements.get(id);
    }
  }, {get(target, key) {
    return target[key] || {state: [{checked: true, value: 'once'}]};
  }});
  const timers = new Map();
  let next = 0;
  const context = vm.createContext({document, navigator: {userAgent: 'control-verification'},
    Image: class {constructor() {this.src = '';}},
    setTimeout(callback) {callback();},
    setInterval(callback) {const id = ++next; timers.set(id, callback); return id;},
    clearInterval(id) {timers.delete(id);}});
  for (const [, script] of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)) {
    new vm.Script(script).runInContext(context);
  }
  const name = Object.keys(context).find(key => /^anim[0-9a-f]{32}$/.test(key));
  assert(name, 'Animation not initialized');
  const animation = context[name];
  assert(html.includes(`id="${animation.img_id}"`), 'Image target missing');
  assert(html.includes(`id="${animation.slider_id}"`), 'Slider target missing');
  assert.equal(animation.frames.length, 64);
  for (const frame of animation.frames) {
    const prefix = 'data:image/png;base64,';
    assert(frame.src.startsWith(prefix));
    const png = Buffer.from(frame.src.slice(prefix.length), 'base64');
    assert(png.length > 1000);
    assert.equal(png.subarray(1, 4).toString(), 'PNG');
  }
  assert.notEqual(animation.frames[0].src, animation.frames[63].src);
  animation.next_frame(); assert.equal(animation.current_frame, 1);
  animation.previous_frame(); assert.equal(animation.current_frame, 0);
  animation.last_frame(); assert.equal(animation.current_frame, 63);
  animation.first_frame(); assert.equal(animation.current_frame, 0);
  animation.play_animation(); assert.equal(animation.direction, 1);
  timers.get(animation.timer)(); assert.equal(animation.current_frame, 1);
  animation.pause_animation(); assert.equal(animation.direction, 0); assert.equal(timers.size, 0);
  animation.last_frame(); animation.reverse_animation();
  timers.get(animation.timer)(); assert.equal(animation.current_frame, 62);
  animation.pause_animation();
  const speed = animation.interval; animation.faster(); assert(animation.interval < speed);
  animation.slower(); assert(Math.abs(animation.interval-speed) < 1e-9);
  animation.set_frame(17);
  assert.equal(document.getElementById(animation.img_id).src, animation.frames[17].src);
  animation.last_frame(); animation.anim_step_forward(); assert.equal(animation.current_frame, 63);
  animation.first_frame(); animation.anim_step_reverse(); assert.equal(animation.current_frame, 0);
  console.log(`3.${task}: 64 PNG frames; play/pause, reverse, slider and speed: OK`);
}
