import os

with open(r"n:\PROJECTS\INSIST\sih26034\backend\static_ui.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace removePhoto and resetInspection functions
old_remove = """    function removePhoto(idx) {
      uploadedPhotos.splice(idx, 1);
      // Re-index view names
      uploadedPhotos.forEach((p, i) => {
        p.view = 'Photo ' + (i + 1);
      });
      renderPhotoTray();
      if (curStep === 2) renderQualityStep();
    }"""

new_remove = """    async function removePhoto(idx) {
      const p = uploadedPhotos[idx];
      if (p && inspId && p.id && !p.id.startsWith('IMG-DEMO')) {
        try {
          await fetch('/api/inspections/' + inspId + '/images/' + p.id, { method: 'DELETE' });
        } catch (e) {
          console.error('Delete error:', e);
        }
      }
      uploadedPhotos.splice(idx, 1);
      uploadedPhotos.forEach((item, i) => {
        item.view = 'Photo ' + (i + 1);
      });
      renderPhotoTray();
      if (curStep === 2) renderQualityStep();
    }"""

html = html.replace(old_remove, new_remove)

with open(r"n:\PROJECTS\INSIST\sih26034\backend\static_ui.html", "w", encoding="utf-8") as f:
    f.write(html)

print("static_ui.html updated to synchronize backend deletion with UI photo removal")
