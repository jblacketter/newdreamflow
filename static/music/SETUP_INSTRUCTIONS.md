# Background Music Setup Instructions

The background music feature is configured but needs actual audio files to work.

## Quick Test

1. To test if the music player is working, you can:
   - Go to your Profile
   - Select any background music option (e.g., "Ocean Waves")
   - Save changes
   - You'll see a music button (🎵) in the bottom right corner
   - If the button turns red (❌), it means the audio file is missing

## Adding Music Files

You need to add MP3 files to the `/static/music/` directory with these exact filenames:

- `ambient_forest.mp3` - Forest ambience sounds
- `meditation_bells.mp3` - Soft meditation bells
- `ocean_waves.mp3` - Ocean wave sounds
- `rain_sounds.mp3` - Gentle rain
- `tibetan_bowls.mp3` - Tibetan singing bowls
- `white_noise.mp3` - White noise for focus

## Free Sound Resources

You can download royalty-free ambient sounds from:

1. **Freesound.org** - Community database of Creative Commons sounds
2. **Zapsplat.com** - Free sounds with account
3. **Pixabay Music** - No attribution required
4. **YouTube Audio Library** - Free music and sound effects
5. **archive.org** - Public domain recordings

## Creating Test Files

If you just want to test the feature, you can:

1. Open `/static/music/test_sound.html` in your browser
2. Generate test tones for each sound type
3. Save them with the correct filenames

## File Requirements

- Format: MP3 (preferred), OGG, or WAV
- Duration: Ideally 3-10 minutes (will loop automatically)
- Size: Keep under 10MB per file
- Quality: 128kbps MP3 is sufficient

## Troubleshooting

1. Check browser console for errors (F12 > Console)
2. Verify files exist: `ls static/music/`
3. Try running `python manage.py collectstatic`
4. Make sure your selected music in Profile matches a filename
5. Check volume slider in Profile isn't set to 0

The music player will show:
- 🎵 when stopped
- ⏸️ when playing
- ❌ if file not found

## Note

The app works perfectly fine without music files - this is just an enhancement for ambiance while journaling.