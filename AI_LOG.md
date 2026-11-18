# AI_LOG.md — Blaze Breakers
## 1. วัตถุประสงค์

บันทึกนี้ระบุว่าส่วนไหนของโปรเจกต์ใช้ AI ช่วย และส่วนไหนทีมทำเอง เพื่อใช้ประกอบการสอบ Oral Defense ของรายวิชา SF211

**สรุปสั้น ๆ:**

- **ทีมออกแบบคลาสทั้งหมดเอง** ได้แก่ คลาสที่มี, หน้าที่ของแต่ละคลาส, attribute/method หลัก, ความสัมพันธ์ (inheritance / composition) และการเลือกใช้ pattern
- **AI ช่วยส่วนใหญ่ในงาน design** (ภาพ Pixel Art, ฉาก, HUD, หน้าจอ overlay) **และช่วยเขียน function/method หลายตัว** ภายในคลาสที่ทีมออกแบบไว้แล้ว

## 2. เครื่องมือ AI ที่ใช้

| เครื่องมือ | ใช้ทำอะไร |
| ChatGPT (OpenAI) | ร่างโค้ดวาด Pixel Art และ UI, เขียน function ตาม spec ที่ทีมกำหนด, อธิบายหลัก OOP , ทบทวน Rubric, ช่วยจัดไฟล์และเอกสาร |

## 3. ส่วนที่ทีมทำเอง: การออกแบบคลาส

ทีมกำหนดโครงสร้างคลาสและความสัมพันธ์ทั้งหมดเอง AI ไม่ได้เป็นผู้เลือกว่าต้องมีคลาสอะไร หรือคลาสไหนสืบทอดจากคลาสไหน

| คลาส | โมดูล | หน้าที่ที่ทีมกำหนด | หลัก OOP ที่ทีมตั้งใจแสดง |
| `GameObject(ABC)` | `entities/base.py` | สัญญาของ Sprite ทุกตัว: ต้องมี `update(dt)` และ `draw()` | Abstraction, ABC |
| `Room` | `entities/room.py` | ตำแหน่งและภาพของห้อง, บังคับกติกา "ดับไฟก่อนจึงช่วยคนได้" | Composition (มี `RoomFire` และ `Victim`) |
| `RoomFire` | `entities/room.py` | ความแรงของไฟในห้อง: จุดไฟ, ฉีดน้ำ, จำกัดค่า 0–1.7 | Encapsulation (property `intensity`) |
| `Victim` | `entities/room.py` | คนในห้อง: ความคืบหน้าในการช่วย และสถานะว่าช่วยแล้วหรือยัง | แยกหน้าที่ออกจาก `Room` |
| `Firefighter` | `entities/firefighter.py` | ผู้เล่น: เดินระหว่างห้อง, ชีวิต, ช่วงอมตะหลังโดนโจมตี | Encapsulation (property `lives`) |
| `Hazard` | `entities/hazards.py` | คลาสแม่ของสิ่งอันตราย มี hitbox ร่วมกัน | Inheritance |
| `Debris`, `Fireball` | `entities/hazards.py` | สิ่งอันตราย 2 แบบที่เคลื่อนที่ต่างกัน | Polymorphism (override `update()`) |
| `FireDemon` | `entities/demon.py` | ศัตรูที่เคลื่อนที่และสร้าง `Fireball` | Factory Method (`throw_fire`) |
| `Particle` | `entities/particle.py` | เอฟเฟกต์ชั่วคราว ลบตัวเองเมื่อหมดอายุ | Polymorphism ผ่าน `Group.update()` |
| `ScoreManager`, `NoticeManager` | `core/score.py` | ผู้ฟัง event เดียวกัน: ตัวหนึ่งนับคะแนน อีกตัวแสดงข้อความ | Observer |
| `GameState(ABC)` + `MenuState`, `PlayState`, `PauseState`, `GameOverState` | `core/states.py` | หน้าจอแต่ละสถานะ จัดการด้วย state stack | State Pattern |
| `Game` | `core/game.py` | game loop, state stack, ส่ง event ให้ observer | ศูนย์กลางของเกม |
| `Scene` | `core/scene.py` | รวมโค้ดวาดฉากและ HUD ที่หลาย state ใช้ร่วมกัน | แยกงานวาดออกจาก gameplay |

**ตัวอย่างการตัดสินใจที่ทีมทำเอง:**

- เลือกแยก "ห้องที่ติดไฟ" กับ "คนในห้อง" เป็นคลาส `RoomFire` และ `Victim` ที่ `Room` ประกอบไว้ แทนการใส่ทุกอย่างไว้ใน `Room` คลาสเดียว และไม่ใช้ inheritance ระหว่างห้องกับคน
- ให้ `Debris` และ `Fireball` สืบทอด `Hazard` เพื่อใช้ hitbox ร่วมกัน แต่เคลื่อนที่ต่างกัน
- ใช้ custom event + observer เพื่อไม่ให้ gameplay ไปแก้คะแนนตรง ๆ
- ใช้ state stack เพื่อให้ Pause ซ้อนบน Play ได้โดยไม่ล้างคะแนนและตำแหน่ง

## 4. ส่วนที่ AI ช่วย

### 4.1 Design (ภาพและ UI) — ส่วนที่ใช้ AI มากที่สุด

| ส่วน | ไฟล์ / method | AI ช่วยอะไร |
|---|---|---|
| ฉากอาคารและฉากหลัง | `Scene.draw_building()` | ร่างโค้ดวาดท้องฟ้ากลางคืน, ตึกเงา, อาคารอิฐ 5 คอลัมน์, ประตู, รถดับเพลิง |
| HUD | `Scene.draw_hud()`, `draw_heart()` | จัดวาง SCORE / TIME / HEAT / หัวใจ / แถบล่าง และวาดหัวใจแบบ pixel |
| หน้าจอ overlay | `Scene.draw_overlay()` | กรอบเมนู, Pause, Game Over และปุ่ม |
| ฟังก์ชันช่วยวาด | `block()`, `text()` | วาดสี่เหลี่ยมแบบ pixel และตัวอักษรมีเงา |
| Sprite ผู้เล่น | `Firefighter.draw()` | ภาพนักดับเพลิง, เอฟเฟกต์ฉีดน้ำ, แถบความคืบหน้า, กะพริบตอนอมตะ |
| Sprite ห้อง / ไฟ / คน | `Room.draw()`, `RoomFire.draw()`, `Victim.draw()` | หน้าต่างห้อง, เปลวไฟเคลื่อนไหว, ควัน, คนโบกมือพร้อมป้าย HELP! |
| Sprite ศัตรูและสิ่งอันตราย | `FireDemon.draw()`, `Debris.draw()`, `Fireball.draw()`, `Particle.draw()` | ภาพปีศาจไฟ, เศษอิฐ, ลูกไฟ, อนุภาค |
| ชุดสี | `config.py` | เสนอชุดสี Pixel Art (`INK`, `GOLD`, `FIRE`, `BLUE`, `MINT` ฯลฯ) |

### 4.2 Function / method ที่ AI ช่วยเขียน

ทีมกำหนดชื่อ หน้าที่ และตำแหน่งของ method ใน class diagram ก่อน แล้วให้ AI ช่วยเขียนส่วน implementation

| Function / method | ไฟล์ | AI ช่วยอะไร |
|---|---|---|
| `PlayState._spread_fire()` | `core/states.py` | ตรรกะไฟลามไปห้องข้างเคียง (ระยะ Manhattan = 1) |
| `PlayState._spawn_fireball()`, `_spawn_debris()`, `_spawn_victim()` | `core/states.py` | สุ่มตำแหน่งเกิด โดยให้มีโอกาสเล็งตำแหน่งผู้เล่น |
| `PlayState._collisions()` | `core/states.py` | ใช้ `groupcollide` กับ swept hitbox และจัดการลูกไฟที่ตกถึงห้อง |
| `PlayState.update()` (ส่วน timer) | `core/states.py` | สูตรลดเวลาเกิดของสิ่งอันตรายตามระดับ `threat` |
| `PlayState.threat` | `core/states.py` | สูตรเพิ่มความยากทุก 35 วินาที (สูงสุด 10) |
| `PlayState._scatter()` | `core/states.py` | สร้างอนุภาค และจำกัดจำนวนไม่เกิน 130 ตัว |
| `Fireball.update()` | `entities/hazards.py` | วิถีโค้งจากปีศาจไปยังห้องเป้าหมาย |
| `Hazard.swept_hitbox`, `Firefighter.swept_hitbox` | `entities/` | รวม hitbox ของเฟรมก่อนและเฟรมปัจจุบัน เพื่อไม่ให้การชนหลุดตอนเคลื่อนที่เร็ว |
| `Firefighter.update()` | `entities/firefighter.py` | การเคลื่อนที่แบบนุ่มนวล (lerp) ไปยังห้องเป้าหมาย |
| `FireDemon.update()` | `entities/demon.py` | การเคลื่อนที่แบบคลื่น sin |
| `ScoreManager._read_best()`, `save()` | `core/score.py` | อ่าน/เขียน high score เป็น JSON และกันโปรแกรมพังเมื่อไฟล์เสีย |

## 5. ตัวอย่าง prompt ที่ใช้

**prompt จริงจากการสนทนา (ย่อ):**

- "จากโค้ด firefighter จากโฟลเดอร์นี้ ถ้าจะอิงตามหลัก OOP ที่อาจารย์สอน ควรเพิ่ม function หรือลดอะไรบ้าง"
- "แล้ว function ของเกม เช่น debris หรือ การช่วยคน"
- "อยากให้ ห้องที่ติดไฟ และ คนที่อยู่ในห้องแยก class กัน" 
- "ออกแบบ Graphic design คร่าวๆให้หน่อย"
- "ช่วยร่าง AI_LOG.md,README.md,UML ให้หน่อย"

**ลักษณะคำขอด้าน design (สรุปความ):**

- ขอให้วาดตัวละคร / ห้อง / ปีศาจไฟเป็น Pixel Art ด้วยคำสั่ง `pygame.draw` บน Surface ขนาดที่กำหนด
- ขอให้จัด HUD ให้แสดงคะแนน เวลา ระดับความยาก และหัวใจ 3 ดวง
- ขอให้ทำหน้าจอเมนู / Pause / Game Over ในโทนสีเดียวกัน

## 6. สิ่งที่ทีมตรวจสอบ / ปรับเองหลังได้โค้ดจาก AI

- ตรวจว่าโค้ดที่ AI เขียนอยู่ในคลาสและ method ตามที่ออกแบบไว้ ไม่เพิ่มคลาสใหม่หรือเปลี่ยนความสัมพันธ์เอง
- หลังแยก `RoomFire` / `Victim` ยังคง property `Room.fire` และ `Room.rescue_progress` ไว้ เพื่อให้โค้ดส่วนอื่นไม่ต้องแก้
- ปรับตัวเลขความยาก (ความเร็ว Debris, เวลาเกิด Fireball, ช่วงอมตะ) จากการเล่นจริง
- ทีมอธิบาย method ที่ AI ช่วยเขียนได้เอง และพร้อมตอบคำถามระหว่างสอบ

## 7. บันทึกการทดสอบ

| Test | ผล (PASS/FAIL) | วันที่ / ผู้ทดสอบ / หมายเหตุ |
| `python main.py --check` (unit tests ทั้งหมด) | | |
| เปิดเกมและแสดง Menu | | |
| เดินด้วย Arrows / WASD | | |
| ดับไฟ (+100) | | |
| ช่วยคนหลังดับไฟ (+250) | | |
| โดน Debris / Fireball แล้วเสียชีวิต และมีช่วงอมตะ | | |
| Pause / Resume และ Restart | | |
| High Score ยังอยู่หลังปิดเกมแล้วเปิดใหม่ | | |