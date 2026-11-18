## 1. Prerequisites / สิ่งที่ต้องติดตั้ง

- Python 3.11 ขึ้นไป (ใช้ Python 3.14 บน Windows ได้ ถ้ามี pygame-ce รุ่นที่รองรับ)
- `pygame-ce` ตาม `requirements.txt`
- ไม่ต้องดาวน์โหลดไฟล์รูปหรือเสียงเพิ่มเติม ภาพ Pixel Art ถูกวาดจากคำสั่ง Pygame

## 2. Installation / วิธีติดตั้ง

เปิด Terminal หรือ PowerShell **ในโฟลเดอร์หลักที่มี `main.py`** แล้วใช้:

```powershell
py -3.14 -m pip install -r requirements.txt
py -3.14 main.py
```

ถ้าใช้คำสั่ง `python` แทน `py` หรือใช้ Python รุ่นอื่น:

```bash
python -m pip install -r requirements.txt
python main.py
```

เมื่อติดตั้งสำเร็จ โปรแกรมจะเปิดหน้าต่างเกม (หน้าจอ 640 × 960 pixels จากการขยาย Canvas 320 × 480 เป็น 2 เท่า)

## 3. Controls / ปุ่มควบคุม

| ปุ่ม | การทำงาน |
|---|---|
| Enter หรือ Space ที่ Menu | เริ่มเล่น |
| Arrow Keys / W A S D | เคลื่อนย้ายระหว่างห้อง |
| กด Space หรือ J ค้าง | ฉีดน้ำดับไฟ; ถ้าไม่มีไฟและมีคนอยู่ จะช่วยคน |
| กด E ค้าง | ช่วยคนเมื่อดับไฟแล้ว |
| P | Pause / Resume |
| Esc ระหว่างเล่น | กลับ Menu และบันทึก High Score |
| P หรือ Esc เมื่อ Pause | เล่นต่อ |
| R หรือ Enter เมื่อ Game Over | เริ่มเกมใหม่ |
| M หรือ Esc เมื่อ Game Over | กลับ Menu |
| Esc ที่ Menu หรือปิดหน้าต่าง | ออกเกม |

**กติกา:** เริ่มต้นมี 3 ชีวิต ต้องดับไฟในห้องให้หมดก่อน จึงจะช่วยคนในห้องนั้นได้; โดน `Debris` หรือ `Fireball` จะเสียชีวิต (มีช่วงป้องกันการโดนซ้ำชั่วคราว); ชีวิตหมดจบเกม

## 4. Scoring / คะแนน

| เหตุการณ์ | คะแนน |
|---|---:|
| ดับไฟหนึ่งห้องสำเร็จ (`FIRE_OUT`) | +100 |
| ช่วยคนสำเร็จ (`PERSON_SAVED`) | +250 |
| อยู่รอดครบทุก 10 วินาที (`SURVIVAL_BONUS`) | +20 |

`ScoreManager` จะบันทึกคะแนนสูงสุดใน `endless_highscore.json` ซึ่ง **ถูกสร้างโดยอัตโนมัติเมื่อเล่น** ไม่จำเป็นต้องใส่คะแนนตัวอย่างในไฟล์ส่งงาน

## 5. Project Structure / โครงสร้างโปรเจกต์

```text
FireRescue_SF211_Submission/
├── main.py                 # จุดเริ่มต้นเกม และ --check
├── config.py               # ขนาดหน้าจอ, พิกัดห้อง, สี
├── requirements.txt        # pygame-ce
├── README.md               # เอกสารนี้: วิธีติดตั้ง/เล่น/โครงสร้าง
├── AI_LOG.md               # บันทึกการใช้ AI (ต้องตรวจและเติมบันทึกทีม)
├── core/
│   ├── __init__.py
│   ├── game.py             # Game loop, state stack, dispatch events
│   ├── states.py           # GameState, MenuState, PlayState, PauseState, GameOverState
│   ├── events.py           # pygame custom events
│   ├── score.py            # ScoreManager, NoticeManager (Observers)
│   └── scene.py            # ฉากและ Pixel Art UI
├── entities/
│   ├── __init__.py
│   ├── base.py             # GameObject(ABC)
│   ├── room.py             # Room + RoomFire + Victim (Composition)
│   ├── firefighter.py      # Firefighter (player)
│   ├── hazards.py          # Hazard, Debris, Fireball
│   ├── demon.py            # FireDemon
│   └── particle.py         # Particle effect
├── docs/
│   ├── class-diagram.png   # UML Class Diagram ที่ใช้ส่งงาน
│   └── class-diagram.dot   # ต้นฉบับ UML สำหรับปรับแก้ด้วย Graphviz
└── tests/
    ├── __init__.py
    └── test_game.py        # ตรวจ ABC, การดับไฟ, ช่วยคน, Debris, State, High Score
```