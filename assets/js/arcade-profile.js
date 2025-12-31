/**
 * ARCADE NEXUS - PILOT PROFILE SYSTEM
 * V4.0 Hyper Edition
 * Handles local stats, ranks, and the holographic UI overlay.
 */

const ArcadeProfile = {

    // --- State & Config ---
    data: {
        xp: 0,
        rankIndex: 0,
        gamesPlayed: 0,
        totalScore: 0,
        favoriteGame: 'None',
        scores: {
            'cyber-pong': 0,
            'system-defense': 0,
            'neon-snake': 0,
            'cyber-breaker': 0,
            'void-runner': 0
        },
        playCounts: {
            'cyber-pong': 0,
            'system-defense': 0,
            'neon-snake': 0,
            'cyber-breaker': 0,
            'void-runner': 0
        },
        achievements: [] // Strings of unlocked achievements
    },

    ranks: [
        { name: "Cadet", xp: 0, color: "#888" },
        { name: "Pixel Scout", xp: 500, color: "#44f580" },
        { name: "Neon Rider", xp: 1500, color: "#00f0ff" },
        { name: "Cyber Knight", xp: 3000, color: "#ff003c" },
        { name: "System Breaker", xp: 6000, color: "#d300ff" },
        { name: "Void Walker", xp: 10000, color: "#ffd700" },
        { name: "Arcade Legend", xp: 20000, color: "#fff" },
        { name: "Hyper God", xp: 50000, color: "#ff9900" }
    ],

    achievementsList: [
        { id: 'first_blood', name: 'First Byte', desc: 'Play your first game.' },
        { id: 'high_roller', name: 'High Roller', desc: 'Score 1000+ points in any game.' },
        { id: 'jack_of_all', name: 'Jack of All Trades', desc: 'Play all 5 games at least once.' },
        { id: 'addict', name: 'System Addict', desc: 'Play 50 total games.' },
        { id: 'void_master', name: 'Void Master', desc: 'Reach 5000m in Void Runner.' }
    ],

    init() {
        this.load();
        this.injectUI();
        this.updateRank();
        console.log("Arcade Nexus Profile System Online // v4.0");
    },

    // --- Persistence ---
    load() {
        const saved = localStorage.getItem('nexus_profile_v4');
        if (saved) {
            this.data = { ...this.data, ...JSON.parse(saved) };
        }
    },

    save() {
        this.updateRank();
        localStorage.setItem('nexus_profile_v4', JSON.stringify(this.data));
    },

    // --- Logic ---
    reportGame(gameId, score) {
        this.data.gamesPlayed++;
        this.data.totalScore += Math.floor(score);

        // Update Game Specifics
        if (!this.data.scores[gameId] || score > this.data.scores[gameId]) {
            this.data.scores[gameId] = Math.floor(score);
        }
        this.data.playCounts[gameId] = (this.data.playCounts[gameId] || 0) + 1;

        // Calc Favorite
        let maxPlays = 0;
        for (let g in this.data.playCounts) {
            if (this.data.playCounts[g] > maxPlays) {
                maxPlays = this.data.playCounts[g];
                this.data.favoriteGame = g.replace('-', ' ').toUpperCase();
            }
        }

        // XP Calculation (Roughly 1 XP per 10 score, varies by game balance)
        // Normalize score impact
        let xpGain = Math.floor(score / 5);
        if (gameId === 'void-runner') xpGain = Math.floor(score / 5); // Meters
        if (gameId === 'cyber-pong') xpGain = score * 50; // Goals are rare
        if (gameId === 'neon-snake') xpGain = score * 2;
        if (gameId === 'system-defense') xpGain = Math.floor(score / 10);

        // Cap single game XP to avoid exploits? Nah, let them grind.
        this.data.xp += xpGain;

        this.checkUnlockables(gameId, score);
        this.save();
        this.showToast(`+${xpGain} XP SAVED`);
    },

    checkUnlockables(gameId, score) {
        const unlock = (id) => {
            if (!this.data.achievements.includes(id)) {
                this.data.achievements.push(id);
                this.showToast(`ACHIEVEMENT: ${this.achievementsList.find(a => a.id === id).name}`);
            }
        };

        unlock('first_blood'); // If they played
        if (score >= 1000) unlock('high_roller');
        if (this.data.gamesPlayed >= 50) unlock('addict');
        if (gameId === 'void-runner' && score >= 5000) unlock('void_master');

        // Check Jack of All
        let allPlayed = true;
        for (let g in this.data.playCounts) { if (this.data.playCounts[g] === 0) allPlayed = false; }
        if (allPlayed) unlock('jack_of_all');
    },

    updateRank() {
        for (let i = 0; i < this.ranks.length; i++) {
            if (this.data.xp >= this.ranks[i].xp) {
                this.data.rankIndex = i;
            }
        }
    },

    getHitRate() {
        // Fake a "Skill Rating" based on average consistency or just XP/Games
        if (this.data.gamesPlayed === 0) return 0;
        let skill = Math.min(100, (this.data.totalScore / this.data.gamesPlayed) / 10);
        return Math.floor(skill) + "%";
    },

    // --- UI System ---
    injectUI() {
        // Prevent doubles
        if (document.getElementById('nexus-profile-modal')) return;

        // Styles
        const css = `
            /* Profile Modal Styles */
            #nexus-profile-modal {
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                z-index: 9999; display: flex; justify-content: center; align-items: center;
                background: rgba(0,0,0,0.8); backdrop-filter: blur(10px);
                opacity: 0; pointer-events: none; transition: 0.3s;
                padding: 20px; box-sizing: border-box;
            }
            #nexus-profile-modal.active { opacity: 1; pointer-events: auto; }
            
            .nexus-card {
                width: 700px; max-width: 100%; height: 450px;
                background: linear-gradient(135deg, rgba(5,5,16,0.95), rgba(0,0,0,0.98));
                border: 2px solid var(--neon-blue, #00f0ff);
                border-radius: 20px;
                display: flex; overflow: hidden;
                box-shadow: 0 0 50px rgba(0, 240, 255, 0.15);
                position: relative;
                transform: perspective(1000px) rotateX(0deg) rotateY(0deg);
                transition: transform 0.1s;
                font-family: 'Rajdhani', sans-serif;
                color: #fff;
            }

            /* Animations */
            @keyframes scanline { 0% {top:-10%} 100% {top:110%} }
            .nexus-scan {
                position: absolute; top: 0; left: 0; width: 100%; height: 2px;
                background: rgba(0, 240, 255, 0.5);
                box-shadow: 0 0 10px var(--neon-blue, #00f0ff);
                animation: scanline 2s infinite linear;
                pointer-events: none; opacity: 0.3;
            }

            /* Layout */
            .nexus-left { width: 40%; background: rgba(255,255,255,0.02); padding: 30px; display: flex; flex-direction: column; align-items: center; justify-content: center; border-right: 1px solid rgba(255,255,255,0.1); }
            .nexus-right { width: 60%; padding: 30px; position:relative; }

            .nexus-avatar {
                width: 120px; height: 120px; border-radius: 50%;
                border: 3px solid var(--neon-green, #44f580);
                background: url('https://api.dicebear.com/9.x/bottts-neutral/svg?seed=NexusPilot'); 
                background-size: cover;
                margin-bottom: 20px;
                box-shadow: 0 0 20px var(--neon-green, #44f580);
            }

            .nexus-rank { font-family: 'Science Gothic', sans-serif; font-size: 1.8rem; text-transform: uppercase; margin: 0; text-align: center; line-height:1; }
            .nexus-xp { font-size: 1rem; color: #888; margin-top: 5px; letter-spacing: 2px; }
            
            .nexus-stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
            .nexus-stat-item { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; border-left: 3px solid #555; }
            .nexus-stat-label { font-size: 0.8rem; color: #aaa; text-transform: uppercase; letter-spacing: 1px; display: block; }
            .nexus-stat-val { font-size: 1.5rem; font-weight: bold; color: #fff; }

            .nexus-actions { position: absolute; bottom: 30px; right: 30px; display: flex; gap: 10px; }
            .nexus-btn {
                background: transparent; border: 1px solid var(--neon-red, #ff003c);
                color: var(--neon-red, #ff003c); padding: 10px 25px;
                cursor: pointer; text-transform: uppercase; font-weight: bold;
                transition: 0.2s; font-family: 'Rajdhani';
            }
            .nexus-btn:hover { background: var(--neon-red, #ff003c); color: #000; }

            /* Toast */
            #nexus-toast {
                position: fixed; bottom: 30px; right: 30px;
                background: rgba(0,0,0,0.9); border: 1px solid var(--neon-green, #44f580);
                padding: 15px 30px; color: var(--neon-green, #44f580);
                font-family: 'Science Gothic'; font-size: 1.2rem;
                transform: translateX(200%); transition: 0.3s; z-index: 10000;
                display: flex; align-items: center; gap: 10px;
            }
            #nexus-toast.active { transform: translateX(0); }

            /* Responsive */
            @media (max-width: 768px) {
                .nexus-card { flex-direction: column; height: auto; max-width: 100%; }
                .nexus-left { width: 100%; border-right: none; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 20px; }
                .nexus-right { width: 100%; padding: 20px; padding-bottom: 80px; }
                .nexus-avatar { width: 80px; height: 80px; }
                .nexus-rank { font-size: 1.5rem; }
                .nexus-stat-grid { grid-template-columns: 1fr; gap: 10px; }
                .nexus-stat-item { padding: 10px; }
                .nexus-actions { width: 100%; right: 0; bottom: 20px; justify-content: center; }
            }
        `;
        const style = document.createElement('style');
        style.innerHTML = css;
        document.head.appendChild(style);

        // HTML
        const modal = document.createElement('div');
        modal.id = 'nexus-profile-modal';
        modal.innerHTML = `
            <div class="nexus-card" id="nexus-tilt-card">
                <div class="nexus-scan"></div>
                <div class="nexus-left">
                    <div class="nexus-avatar" id="p-avatar"></div>
                    <h2 class="nexus-rank" id="p-rank">CADET</h2>
                    <div class="nexus-xp" id="p-xp">XP: 0</div>
                </div>
                <div class="nexus-right">
                    <h3 style="margin:0 0 20px 0; font-family:'Science Gothic'; letter-spacing:2px; border-bottom:1px solid #333; padding-bottom:10px;">PILOT STATISTICS</h3>
                    
                    <div class="nexus-stat-grid">
                        <div class="nexus-stat-item" style="border-color:var(--neon-green)">
                            <span class="nexus-stat-label">Total Score</span>
                            <span class="nexus-stat-val" id="p-score">0</span>
                        </div>
                        <div class="nexus-stat-item" style="border-color:var(--neon-blue)">
                            <span class="nexus-stat-label">Games Played</span>
                            <span class="nexus-stat-val" id="p-games">0</span>
                        </div>
                        <div class="nexus-stat-item" style="border-color:var(--neon-red)">
                            <span class="nexus-stat-label">Achievements</span>
                            <span class="nexus-stat-val" id="p-badges">0/5</span>
                        </div>
                         <div class="nexus-stat-item" style="border-color:#ffd700">
                            <span class="nexus-stat-label">Favorite</span>
                            <span class="nexus-stat-val" id="p-fav" style="font-size:1rem; line-height:1.5em">None</span>
                        </div>
                    </div>

                    <div class="nexus-actions">
                        <button class="nexus-btn" onclick="ArcadeProfile.close()">CLOSE</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Toast
        const toast = document.createElement('div');
        toast.id = 'nexus-toast';
        toast.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> <span>SAVED</span>';
        document.body.appendChild(toast);

        // 3D Tilt Effect
        const card = document.getElementById('nexus-tilt-card');
        modal.addEventListener('mousemove', (e) => {
            let xAxis = (window.innerWidth / 2 - e.pageX) / 25;
            let yAxis = (window.innerHeight / 2 - e.pageY) / 25;
            card.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
        });
    },

    open() {
        this.load();
        const r = this.ranks[this.data.rankIndex];

        // Populate Data
        document.getElementById('p-rank').innerText = r.name;
        document.getElementById('p-rank').style.color = r.color;
        document.getElementById('p-avatar').style.borderColor = r.color;
        document.getElementById('p-xp').innerText = `XP: ${this.data.xp.toLocaleString()}`;

        document.getElementById('p-score').innerText = this.data.totalScore.toLocaleString();
        document.getElementById('p-games').innerText = this.data.gamesPlayed;
        document.getElementById('p-badges').innerText = `${this.data.achievements.length}/${this.achievementsList.length}`;
        document.getElementById('p-fav').innerText = this.data.favoriteGame;

        document.getElementById('nexus-profile-modal').classList.add('active');
    },

    close() {
        document.getElementById('nexus-profile-modal').classList.remove('active');
    },

    showToast(msg) {
        const t = document.getElementById('nexus-toast');
        t.querySelector('span').innerText = msg;
        t.classList.add('active');
        setTimeout(() => t.classList.remove('active'), 3000);
    }
};

// Auto-Init
document.addEventListener('DOMContentLoaded', () => {
    ArcadeProfile.init();
});
