// Client-side highlight -> comment feature for revise page
document.addEventListener('DOMContentLoaded', () => {
	// initialize state for each questionGroup
	document.querySelectorAll('.questionGroup').forEach(group => {
		group.style.position = group.style.position || 'relative';
		const idxInput = group.querySelector('input[id^="highlight_comments-"]');
		const highlightsList = group.querySelector('.highlightsList');
		group._highlights = [];
		if (idxInput && idxInput.value) {
			try { group._highlights = JSON.parse(idxInput.value) || []; } catch (e) { group._highlights = []; }
		}
		renderHighlightsList(group);

		// Listen for text selection inside the group
		group.addEventListener('mouseup', (ev) => {
			const sel = window.getSelection();
			const text = sel && sel.toString().trim();
			if (!text) return;
			// ensure selection is inside this group
			const range = sel.getRangeAt(0);
			if (!group.contains(range.commonAncestorContainer)) return;

			const rect = range.getBoundingClientRect();
			const containerRect = group.getBoundingClientRect();
			const x = rect.left - containerRect.left;
			const y = rect.top - containerRect.top + range.height;

			openCommentBox(group, x, y, text);
			sel.removeAllRanges();
		});
	});

	function openCommentBox(group, x, y, selectedText) {
		// remove any existing transient box
		closeTransientBoxes(group);
		const box = document.createElement('div');
		box.className = 'commentBox';
		box.style.position = 'absolute';
		box.style.left = Math.max(4, x) + 'px';
		box.style.top = Math.max(4, y) + 'px';
		box.style.zIndex = 50;
		box.innerHTML = `
			<div class="cb-header" style="cursor:move;padding:4px;background:#eee;border-bottom:1px solid #ccc;">Comment</div>
			<div style="padding:6px"><div style="font-size:0.9em;margin-bottom:6px;color:#111;"><strong>Selected:</strong> <span class="selectedText"></span></div>
			<textarea class="cb-text" rows="3" style="width:260px"></textarea>
			<div style="margin-top:6px;text-align:right">
				<button type="button" class="cb-save">Save</button>
				<button type="button" class="cb-cancel">Cancel</button>
			</div></div>`;
		box.querySelector('.selectedText').textContent = selectedText;
		group.appendChild(box);

		// dragging
		const header = box.querySelector('.cb-header');
		let drag = null;
		header.addEventListener('mousedown', (e) => {
			drag = {x: e.clientX, y: e.clientY, left: box.offsetLeft, top: box.offsetTop};
			document.addEventListener('mousemove', onDrag);
			document.addEventListener('mouseup', endDrag);
			e.preventDefault();
		});
		function onDrag(e) {
			if (!drag) return;
			const dx = e.clientX - drag.x;
			const dy = e.clientY - drag.y;
			box.style.left = Math.max(0, drag.left + dx) + 'px';
			box.style.top = Math.max(0, drag.top + dy) + 'px';
		}
		function endDrag() { document.removeEventListener('mousemove', onDrag); document.removeEventListener('mouseup', endDrag); drag = null; }

		box.querySelector('.cb-cancel').addEventListener('click', () => { box.remove(); });
		box.querySelector('.cb-save').addEventListener('click', () => {
			const content = box.querySelector('.cb-text').value.trim();
			const sel = box.querySelector('.selectedText').textContent;
			if (!content) return alert('Please enter a comment.');
			const entry = {text: sel, comment: content, top: box.style.top, left: box.style.left};
			group._highlights.push(entry);
			// persist to hidden input
			const idxInput = group.querySelector('input[id^="highlight_comments-"]');
			if (idxInput) idxInput.value = JSON.stringify(group._highlights);
			renderHighlightsList(group);
			box.remove();
		});
	}

	function closeTransientBoxes(group) {
		group.querySelectorAll('.commentBox').forEach(b => b.remove());
	}

	function renderHighlightsList(group) {
		const list = group.querySelector('.highlightsList');
		const idxInput = group.querySelector('input[id^="highlight_comments-"]');
		if (!list) return;
		list.innerHTML = '';
		(group._highlights || []).forEach((h, i) => {
			const item = document.createElement('div');
			item.className = 'hl-item';
			item.style.border = '1px solid #ddd';
			item.style.padding = '6px';
			item.style.marginBottom = '6px';
			item.innerHTML = `<div style="font-size:0.9em;color:#333"><strong>"${escapeHtml(h.text)}"</strong></div>
												<div style="margin-top:4px">${escapeHtml(h.comment)}</div>
												<div style="text-align:right;margin-top:6px">
													<button type="button" class="hl-edit">Edit</button>
													<button type="button" class="hl-delete">Delete</button>
												</div>`;
			list.appendChild(item);
			item.querySelector('.hl-delete').addEventListener('click', () => {
				group._highlights.splice(i,1);
				if (idxInput) idxInput.value = JSON.stringify(group._highlights);
				renderHighlightsList(group);
			});
			item.querySelector('.hl-edit').addEventListener('click', () => {
				openEditBox(group, i);
			});
		});
	}

	function openEditBox(group, index) {
		const h = group._highlights[index];
		if (!h) return;
		// create editable box at stored position if possible
		const box = document.createElement('div');
		box.className = 'commentBox';
		box.style.position = 'absolute';
		box.style.left = h.left || '10px';
		box.style.top = h.top || '10px';
		box.style.zIndex = 50;
		box.innerHTML = `
			<div class="cb-header" style="cursor:move;padding:4px;background:#eee;border-bottom:1px solid #ccc;">Edit Comment</div>
			<div style="padding:6px"><div style="font-size:0.9em;margin-bottom:6px;color:#111;"><strong>Selected:</strong> <span class="selectedText"></span></div>
			<textarea class="cb-text" rows="3" style="width:260px"></textarea>
			<div style="margin-top:6px;text-align:right">
				<button type="button" class="cb-save">Save</button>
				<button type="button" class="cb-cancel">Cancel</button>
			</div></div>`;
		box.querySelector('.selectedText').textContent = h.text;
		box.querySelector('.cb-text').value = h.comment;
		group.appendChild(box);

		// drag
		const header = box.querySelector('.cb-header');
		let drag = null;
		header.addEventListener('mousedown', (e) => {
			drag = {x: e.clientX, y: e.clientY, left: box.offsetLeft, top: box.offsetTop};
			document.addEventListener('mousemove', onDrag);
			document.addEventListener('mouseup', endDrag);
			e.preventDefault();
		});
		function onDrag(e) {
			if (!drag) return;
			const dx = e.clientX - drag.x;
			const dy = e.clientY - drag.y;
			box.style.left = Math.max(0, drag.left + dx) + 'px';
			box.style.top = Math.max(0, drag.top + dy) + 'px';
		}
		function endDrag() { document.removeEventListener('mousemove', onDrag); document.removeEventListener('mouseup', endDrag); drag = null; }

		box.querySelector('.cb-cancel').addEventListener('click', () => { box.remove(); });
		box.querySelector('.cb-save').addEventListener('click', () => {
			const content = box.querySelector('.cb-text').value.trim();
			if (!content) return alert('Please enter a comment.');
			group._highlights[index].comment = content;
			group._highlights[index].top = box.style.top;
			group._highlights[index].left = box.style.left;
			const idxInput = group.querySelector('input[id^="highlight_comments-"]');
			if (idxInput) idxInput.value = JSON.stringify(group._highlights);
			renderHighlightsList(group);
			box.remove();
		});
	}

	function escapeHtml(s){ return String(s).replace(/[&<>"']/g, (c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"})[c]); }

});