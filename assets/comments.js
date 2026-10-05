// Comment box under each creative. Comments are saved by n8n
// (n8n.poulinelectrique.com), which also emails Maggie and posts in Talk.
// Each card's comments are filed under its file name, e.g.
// PEI_IO1-Generac_FR_300x250, so French and English pages share them.
(() => {
  const API = window.EVANOV_API || 'https://n8n.poulinelectrique.com/webhook/';
  const fr = document.documentElement.lang.startsWith('fr');
  const T = fr ? {
    title: 'Commentaires', none: 'Aucun commentaire pour l’instant.',
    name: 'Votre nom', text: 'Votre commentaire', send: 'Envoyer',
    sending: 'Envoi…', sent: 'Merci! Maggie a été avisée.',
    fail: 'Envoi impossible. Réessayez ou écrivez à maggie@poulinelectrique.com.',
    off: 'Les commentaires ne sont pas disponibles pour le moment.', loc: 'fr-CA'
  } : {
    title: 'Comments', none: 'No comments yet.',
    name: 'Your name', text: 'Your comment', send: 'Send',
    sending: 'Sending…', sent: 'Thank you! Maggie has been notified.',
    fail: 'Could not send. Try again or email maggie@poulinelectrique.com.',
    off: 'Comments are not available right now.', loc: 'en-CA'
  };
  const byItem = {}, boxes = [];
  let state = 'loading';
  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  };
  const when = (iso) => new Date(iso).toLocaleString(T.loc, {
    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
  });
  const savedName = () => { try { return localStorage.getItem('evanov-name') || ''; } catch (e) { return ''; } };
  const anchor = (id) => id.replace(/\s+/g, '-');

  function load(list) {
    Object.keys(byItem).forEach(k => delete byItem[k]);
    list.forEach(c => (byItem[c.item] = byItem[c.item] || []).push(c));
  }

  function render(b) {
    const list = byItem[b.id] || [];
    b.count.textContent = list.length ? ' (' + list.length + ')' : '';
    b.root.classList.toggle('has', list.length > 0);
    b.list.textContent = '';
    if (state === 'off') b.list.append(el('li', 'empty', T.off));
    else if (state === 'ready' && !list.length) b.list.append(el('li', 'empty', T.none));
    list.forEach(c => {
      const li = el('li'), who = el('p', 'who');
      who.append(el('b', '', c.name), ' · ' + when(c.at));
      li.append(who, el('p', 'txt', c.text));
      b.list.append(li);
    });
  }

  function attach(card, id) {
    if (card.dataset.cmt) return;
    card.dataset.cmt = '1';
    card.id = anchor(id);
    const root = el('details', 'cmt'), sum = el('summary'), count = el('span', 'n');
    sum.append(el('span', '', T.title), count);
    const list = el('ol', 'cmt-list');
    const form = el('form', 'cmt-form');
    const name = el('input'); name.name = 'name'; name.placeholder = T.name;
    name.maxLength = 60; name.required = true; name.autocomplete = 'name'; name.value = savedName();
    name.setAttribute('aria-label', T.name);
    const text = el('textarea'); text.name = 'text'; text.placeholder = T.text;
    text.maxLength = 2000; text.rows = 3; text.required = true; text.setAttribute('aria-label', T.text);
    const trap = el('input', 'hp'); trap.name = 'website'; trap.tabIndex = -1;
    trap.autocomplete = 'off'; trap.setAttribute('aria-hidden', 'true');
    const send = el('button', '', T.send); send.type = 'submit';
    const status = el('p', 'cmt-status'); status.setAttribute('role', 'status');
    form.append(name, text, trap, send, status);
    root.append(sum, list, form);
    card.append(root);
    const b = { id, root, count, list };
    boxes.push(b);
    render(b);
    if (decodeURIComponent(location.hash.slice(1)) === card.id) {
      root.open = true;
      setTimeout(() => card.scrollIntoView({ block: 'center' }), 300);
    }
    form.addEventListener('submit', (ev) => {
      ev.preventDefault();
      send.disabled = true;
      status.textContent = T.sending;
      try { localStorage.setItem('evanov-name', name.value.trim()); } catch (e) {}
      const body = new URLSearchParams({ item: id, name: name.value, text: text.value,
        website: trap.value, lang: fr ? 'fr' : 'en' });
      fetch(API + 'evanov-comment', { method: 'POST', body })
        .then(r => r.ok ? r.json() : Promise.reject())
        .then(d => {
          if (!d.ok) return Promise.reject();
          state = 'ready';
          load(d.comments || []);
          boxes.forEach(render);
          text.value = '';
          status.textContent = T.sent;
        })
        .catch(() => { status.textContent = T.fail; })
        .finally(() => { send.disabled = false; });
    });
  }

  window.evanovComments = { attach };
  // Creatives already on the page: the comment thread is named after the
  // first download link's file name.
  document.querySelectorAll('main .card').forEach(card => {
    const a = card.querySelector('.dl a');
    if (!a) return;
    const file = decodeURIComponent(a.getAttribute('href').split('/').pop());
    attach(card, file.replace(/\.[^.]+$/, ''));
  });
  fetch(API + 'evanov-comments', { cache: 'no-store' })
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(d => { state = 'ready'; load(d.comments || []); })
    .catch(() => { state = 'off'; })
    .finally(() => boxes.forEach(render));
})();
