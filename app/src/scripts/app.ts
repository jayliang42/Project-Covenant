// Progressive enhancement for every page. Pages are fully readable without it;
// this adds language switching, local progress, quizzes and settings.
import * as store from './store';
import type { LangMode, State } from './store';

type Text = { zh: string; en?: string };
interface LessonInfo { id: string; title: Text; summary: Text; unit: string; minutes: number; url: string }
interface TrackInfo { id: string; color: string; title: Text; url: string; lessons: LessonInfo[]; units: { id: string; title: Text; lessons: string[] }[] }

const RELATED_BRIDGES: Record<string, { id: string; reason: Text }[]> = {
  'curious/01-a-library-of-books': [
    { id: 'seeking/05-manuscripts', reason: { zh: '想查证 · 抄本是怎样保存下来的', en: 'Checking the evidence · How the manuscripts survived' } },
    { id: 'new/01-reading-every-day', reason: { zh: '动手做 · 每天读经 15 分钟', en: 'Try it · Reading 15 minutes a day' } },
  ],
  'curious/02-many-kinds-of-writing': [
    { id: 'deeper/02-reading-the-ot-through-christ', reason: { zh: '读深一点 · 怎样在旧约里读出基督', en: 'Going deeper · Reading the Old Testament through Christ' } },
    { id: 'new/01-reading-every-day', reason: { zh: '动手做 · 开始每天读经', en: 'Try it · Start reading every day' } },
  ],
  'curious/03-how-the-bible-came-to-us': [
    { id: 'seeking/05-manuscripts', reason: { zh: '读深一点 · 死海古卷和抄本比对', en: 'Going deeper · The Dead Sea Scrolls and comparing manuscripts' } },
    { id: 'seeking/04-what-history-can-show', reason: { zh: '想查证 · 考古和史料能说明什么', en: 'Checking the evidence · What archaeology and sources can show' } },
  ],
  'curious/04-one-story': [
    { id: 'deeper/01-covenant-thread', reason: { zh: '读深一点 · 贯穿全书的圣约', en: 'Going deeper · The covenants that run through the Bible' } },
    { id: 'curious/05-creation-and-fall', reason: { zh: '接着读 · 创造和堕落', en: 'Next · Creation and fall' } },
  ],
  'curious/05-creation-and-fall': [
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '相关问题 · 世界上为什么有苦难', en: 'Related question · Why is there suffering?' } },
    { id: 'new/03-i-believe-in-god-the-father', reason: { zh: '相关一课 · 创造天地的主是谁', en: 'Related lesson · Who is the Maker of heaven and earth?' } },
  ],
  'curious/06-who-is-jesus': [
    { id: 'seeking/04-what-history-can-show', reason: { zh: '想查证 · 历史学家怎样看耶稣和空坟墓', en: 'Checking the evidence · Historians on Jesus and the empty tomb' } },
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '相关一课 · 基督是谁，做了什么', en: 'Related lesson · Who Christ is and what he did' } },
  ],
  'curious/07-what-jesus-taught': [
    { id: 'seeking/06-what-it-means-to-believe', reason: { zh: '相关问题 · 恩典和道德努力有什么不同', en: 'Related question · How grace differs from moral effort' } },
    { id: 'new/02-learning-to-pray', reason: { zh: '动手做 · 用主祷文祷告', en: 'Try it · Praying the Lord’s Prayer' } },
  ],
  'seeking/01-questions-are-welcome': [
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '最常问 · 良善的神和苦难', en: 'Most asked · A good God and suffering' } },
    { id: 'curious/01-a-library-of-books', reason: { zh: '入门 · 圣经是一本怎样的书', en: 'First look · What kind of book the Bible is' } },
  ],
  'seeking/02-why-is-there-suffering': [
    { id: 'curious/05-creation-and-fall', reason: { zh: '背景 · 世界为什么又美又痛', en: 'Background · Why the world is both beautiful and broken' } },
    { id: 'new/02-learning-to-pray', reason: { zh: '动手做 · 在困惑和眼泪中怎样祷告', en: 'Try it · Praying in confusion and tears' } },
  ],
  'seeking/03-does-god-exist': [
    { id: 'seeking/04-what-history-can-show', reason: { zh: '接着读 · 历史能说明什么', en: 'Next · What history can show' } },
    { id: 'new/03-i-believe-in-god-the-father', reason: { zh: '相关一课 · 圣经所说的神是怎样的一位', en: 'Related lesson · Who is the God the Bible speaks of?' } },
  ],
  'seeking/04-what-history-can-show': [
    { id: 'deeper/03-second-temple-world', reason: { zh: '背景 · 第二圣殿时期和罗马帝国', en: 'Background · The Second Temple period and the Roman Empire' } },
    { id: 'seeking/05-manuscripts', reason: { zh: '想查证 · 抄本有没有被改过', en: 'Checking the evidence · Were the manuscripts changed?' } },
  ],
  'seeking/05-manuscripts': [
    { id: 'curious/03-how-the-bible-came-to-us', reason: { zh: '概览 · 正典的形成和现代译本', en: 'Overview · How the canon formed, and modern translations' } },
    { id: 'seeking/06-what-it-means-to-believe', reason: { zh: '接着读 · “信”是什么意思', en: 'Next · What it means to believe' } },
  ],
  'seeking/06-what-it-means-to-believe': [
    { id: 'new/01-reading-every-day', reason: { zh: '动手做 · 怎样开始每天读圣经', en: 'Try it · How to start reading daily' } },
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '相关一课 · 耶稣基督和他的救恩', en: 'Related lesson · Jesus Christ and his salvation' } },
  ],
  'new/01-reading-every-day': [
    { id: 'curious/02-many-kinds-of-writing', reason: { zh: '读经工具 · 分辨叙事、诗歌和书信', en: 'Reading tool · Telling narrative, poetry, and letters apart' } },
    { id: 'deeper/04-leading-a-study', reason: { zh: '读深一点 · 观察、解释、应用', en: 'Going deeper · Observation, interpretation, application' } },
  ],
  'new/02-learning-to-pray': [
    { id: 'new/03-i-believe-in-god-the-father', reason: { zh: '相关一课 · 我们祷告时呼求的天父', en: 'Related lesson · The Father we pray to' } },
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '相关问题 · 神是良善的，为什么有苦难', en: 'Related question · If God is good, why is there suffering?' } },
  ],
  'new/03-i-believe-in-god-the-father': [
    { id: 'curious/05-creation-and-fall', reason: { zh: '背景 · 创造的美善和人的堕落', en: 'Background · The goodness of creation and the fall' } },
    { id: 'deeper/01-covenant-thread', reason: { zh: '读深一点 · 神在历史中立的约', en: 'Going deeper · The covenants God made in history' } },
  ],
  'new/04-jesus-christ-his-only-son': [
    { id: 'deeper/02-reading-the-ot-through-christ', reason: { zh: '读深一点 · 旧约怎样指向基督', en: 'Going deeper · How the Old Testament points to Christ' } },
    { id: 'curious/06-who-is-jesus', reason: { zh: '相关一课 · 四福音书里的耶稣', en: 'Related lesson · Jesus in the four Gospels' } },
  ],
  'new/05-baptism-and-communion': [
    { id: 'deeper/01-covenant-thread', reason: { zh: '读深一点 · “用我血所立的新约”从哪里来', en: 'Going deeper · Where “the new covenant in my blood” comes from' } },
    { id: 'deeper/04-leading-a-study', reason: { zh: '动手做 · 和别人一起查经', en: 'Try it · Studying the Bible with others' } },
  ],
  'deeper/01-covenant-thread': [
    { id: 'deeper/02-reading-the-ot-through-christ', reason: { zh: '接着读 · 各个圣约怎样在基督里成全', en: 'Next · How the covenants are fulfilled in Christ' } },
    { id: 'new/05-baptism-and-communion', reason: { zh: '相关一课 · 洗礼和圣餐', en: 'Related lesson · Baptism and the Lord’s Supper' } },
  ],
  'deeper/02-reading-the-ot-through-christ': [
    { id: 'deeper/03-second-temple-world', reason: { zh: '背景 · 第二圣殿时期', en: 'Background · The Second Temple period' } },
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '相关一课 · 信经里的耶稣基督', en: 'Related lesson · Jesus Christ in the Creed' } },
  ],
  'deeper/03-second-temple-world': [
    { id: 'seeking/04-what-history-can-show', reason: { zh: '想查证 · 约瑟夫斯、塔西佗和考古铭文', en: 'Checking the evidence · Josephus, Tacitus, and inscriptions' } },
    { id: 'deeper/04-leading-a-study', reason: { zh: '动手做 · 用历史背景设计查经问题', en: 'Try it · Using historical background to write study questions' } },
  ],
  'deeper/04-leading-a-study': [
    { id: 'new/01-reading-every-day', reason: { zh: '相关一课 · 先养成自己每天读经的习惯', en: 'Related lesson · Build your own daily reading habit first' } },
    { id: 'curious/02-many-kinds-of-writing', reason: { zh: '读经工具 · 帮组员分清叙事和书信', en: 'Reading tool · Helping a group tell narrative from letters' } },
  ],
  'curious/08-how-to-look-up-a-verse': [
    { id: 'new/01-reading-every-day', reason: { zh: '动手做 · 每天读一点圣经', en: 'Try it · Reading a little every day' } },
    { id: 'curious/02-many-kinds-of-writing', reason: { zh: '接着读 · 圣经里的不同文体', en: 'Next · The kinds of writing in the Bible' } },
  ],
  'curious/09-abraham-and-the-promise': [
    { id: 'deeper/01-covenant-thread', reason: { zh: '读深一点 · 亚伯拉罕之约和其他圣约', en: 'Going deeper · The covenant with Abraham and the others' } },
    { id: 'seeking/12-grace', reason: { zh: '相关一课 · 因信被算为义', en: 'Related lesson · Counted righteous by faith' } },
  ],
  'curious/10-out-of-egypt': [
    { id: 'deeper/06-god-dwelling-with-people', reason: { zh: '读深一点 · 会幕和神的同在', en: 'Going deeper · The tabernacle and God’s presence' } },
    { id: 'deeper/11-ancient-near-east', reason: { zh: '背景 · 西奈之约和古代条约', en: 'Background · The Sinai covenant and ancient treaties' } },
  ],
  'curious/11-kings-prophets-exile': [
    { id: 'deeper/08-reading-the-prophets', reason: { zh: '读深一点 · 怎样读先知书', en: 'Going deeper · How to read the prophets' } },
    { id: 'deeper/05-kingdom-of-god', reason: { zh: '读深一点 · 大卫的子孙和神的国', en: 'Going deeper · David’s son and the kingdom of God' } },
  ],
  'curious/12-why-the-cross': [
    { id: 'seeking/11-what-is-sin', reason: { zh: '相关问题 · 圣经说的罪是什么', en: 'Related question · What the Bible means by sin' } },
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '相关一课 · 信经里的受难和复活', en: 'Related lesson · The suffering and resurrection in the Creed' } },
  ],
  'curious/13-the-empty-tomb': [
    { id: 'seeking/09-did-jesus-rise', reason: { zh: '想查证 · 历史学家怎样看复活', en: 'Checking the evidence · How historians see the resurrection' } },
    { id: 'curious/14-the-church-begins', reason: { zh: '接着读 · 教会是怎样开始的', en: 'Next · How the church began' } },
  ],
  'curious/14-the-church-begins': [
    { id: 'deeper/12-pauls-cities', reason: { zh: '背景 · 保罗去过的罗马城市', en: 'Background · The Roman cities Paul visited' } },
    { id: 'new/08-i-believe-in-the-holy-spirit', reason: { zh: '相关一课 · 圣灵是谁', en: 'Related lesson · Who the Holy Spirit is' } },
  ],
  'curious/15-new-heaven-new-earth': [
    { id: 'deeper/10-reading-revelation', reason: { zh: '读深一点 · 怎样读启示录', en: 'Going deeper · How to read Revelation' } },
    { id: 'deeper/06-god-dwelling-with-people', reason: { zh: '读深一点 · 神与人同住', en: 'Going deeper · God living among people' } },
  ],
  'seeking/07-are-all-religions-the-same': [
    { id: 'curious/06-who-is-jesus', reason: { zh: '相关一课 · 耶稣是谁', en: 'Related lesson · Who Jesus is' } },
    { id: 'seeking/12-grace', reason: { zh: '相关一课 · 恩典', en: 'Related lesson · Grace' } },
  ],
  'seeking/08-science-and-faith': [
    { id: 'seeking/03-does-god-exist', reason: { zh: '相关问题 · 有神吗', en: 'Related question · Does God exist?' } },
    { id: 'curious/05-creation-and-fall', reason: { zh: '背景 · 创造和堕落', en: 'Background · Creation and fall' } },
  ],
  'seeking/09-did-jesus-rise': [
    { id: 'curious/13-the-empty-tomb', reason: { zh: '概览 · 福音书怎样记述复活', en: 'Overview · How the Gospels tell of the resurrection' } },
    { id: 'seeking/10-four-gospels', reason: { zh: '接着读 · 为什么有四本福音书', en: 'Next · Why four Gospels' } },
  ],
  'seeking/10-four-gospels': [
    { id: 'seeking/05-manuscripts', reason: { zh: '想查证 · 抄本是怎样保存的', en: 'Checking the evidence · How the manuscripts were kept' } },
    { id: 'curious/08-how-to-look-up-a-verse', reason: { zh: '动手做 · 选一卷福音书开始读', en: 'Try it · Pick a Gospel and start reading' } },
  ],
  'seeking/11-what-is-sin': [
    { id: 'seeking/12-grace', reason: { zh: '接着读 · 恩典', en: 'Next · Grace' } },
    { id: 'new/06-when-i-fail', reason: { zh: '相关一课 · 犯了错怎么办', en: 'Related lesson · What to do when you fail' } },
  ],
  'seeking/12-grace': [
    { id: 'curious/07-what-jesus-taught', reason: { zh: '背景 · 耶稣的比喻', en: 'Background · The parables of Jesus' } },
    { id: 'seeking/06-what-it-means-to-believe', reason: { zh: '接着读 · “信”是什么意思', en: 'Next · What it means to believe' } },
  ],
  'seeking/13-counting-the-cost': [
    { id: 'new/01-reading-every-day', reason: { zh: '动手做 · 开始每天读经', en: 'Try it · Start reading every day' } },
    { id: 'new/10-finding-a-church', reason: { zh: '动手做 · 找一间教会', en: 'Try it · Find a church' } },
  ],
  'new/06-when-i-fail': [
    { id: 'new/02-learning-to-pray', reason: { zh: '相关一课 · 怎样祷告', en: 'Related lesson · How to pray' } },
    { id: 'seeking/12-grace', reason: { zh: '背景 · 为什么得救靠恩典', en: 'Background · Why salvation is by grace' } },
  ],
  'new/07-doubt-and-temptation': [
    { id: 'seeking/01-questions-are-welcome', reason: { zh: '相关一课 · 圣经欢迎人提问', en: 'Related lesson · The Bible welcomes questions' } },
    { id: 'deeper/07-reading-psalms-and-wisdom', reason: { zh: '读深一点 · 用诗篇祷告', en: 'Going deeper · Praying the Psalms' } },
  ],
  'new/08-i-believe-in-the-holy-spirit': [
    { id: 'new/09-one-god-three-persons', reason: { zh: '接着读 · 三位一体', en: 'Next · The Trinity' } },
    { id: 'new/11-gifts-and-serving', reason: { zh: '动手做 · 恩赐和服事', en: 'Try it · Gifts and serving' } },
  ],
  'new/09-one-god-three-persons': [
    { id: 'new/03-i-believe-in-god-the-father', reason: { zh: '相关一课 · 我信天父', en: 'Related lesson · I believe in the Father' } },
    { id: 'deeper/06-god-dwelling-with-people', reason: { zh: '读深一点 · 神与人同住', en: 'Going deeper · God living among people' } },
  ],
  'new/10-finding-a-church': [
    { id: 'new/05-baptism-and-communion', reason: { zh: '相关一课 · 基督徒为什么需要教会', en: 'Related lesson · Why Christians need the church' } },
    { id: 'deeper/13-hard-moments-in-a-group', reason: { zh: '读深一点 · 小组里的难处', en: 'Going deeper · Hard moments in a group' } },
  ],
  'new/11-gifts-and-serving': [
    { id: 'deeper/04-leading-a-study', reason: { zh: '读深一点 · 学习带查经', en: 'Going deeper · Learning to lead a study' } },
    { id: 'new/12-sharing-your-faith', reason: { zh: '接着读 · 怎样谈自己的信仰', en: 'Next · Talking about your faith' } },
  ],
  'new/12-sharing-your-faith': [
    { id: 'seeking/07-are-all-religions-the-same', reason: { zh: '相关问题 · 所有宗教都一样吗', en: 'Related question · Are all religions the same?' } },
    { id: 'seeking/09-did-jesus-rise', reason: { zh: '想查证 · 复活的证据', en: 'Checking the evidence · The evidence for the resurrection' } },
  ],
  'deeper/05-kingdom-of-god': [
    { id: 'curious/07-what-jesus-taught', reason: { zh: '背景 · 耶稣讲的神的国', en: 'Background · Jesus on the kingdom of God' } },
    { id: 'deeper/06-god-dwelling-with-people', reason: { zh: '接着读 · 圣殿主线', en: 'Next · The temple thread' } },
  ],
  'deeper/06-god-dwelling-with-people': [
    { id: 'curious/15-new-heaven-new-earth', reason: { zh: '概览 · 新天新地', en: 'Overview · The new heaven and new earth' } },
    { id: 'deeper/03-second-temple-world', reason: { zh: '背景 · 第二圣殿时期', en: 'Background · The Second Temple period' } },
  ],
  'deeper/07-reading-psalms-and-wisdom': [
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '相关问题 · 苦难和约伯记', en: 'Related question · Suffering and Job' } },
    { id: 'deeper/08-reading-the-prophets', reason: { zh: '接着读 · 怎样读先知书', en: 'Next · How to read the prophets' } },
  ],
  'deeper/08-reading-the-prophets': [
    { id: 'curious/11-kings-prophets-exile', reason: { zh: '背景 · 君王、先知和被掳', en: 'Background · Kings, prophets, and exile' } },
    { id: 'deeper/02-reading-the-ot-through-christ', reason: { zh: '相关一课 · 旧约怎样指向基督', en: 'Related lesson · How the Old Testament points to Christ' } },
  ],
  'deeper/09-reading-the-letters': [
    { id: 'deeper/12-pauls-cities', reason: { zh: '背景 · 保罗书信背后的城市', en: 'Background · The cities behind Paul’s letters' } },
    { id: 'deeper/10-reading-revelation', reason: { zh: '接着读 · 怎样读启示录', en: 'Next · How to read Revelation' } },
  ],
  'deeper/10-reading-revelation': [
    { id: 'curious/15-new-heaven-new-earth', reason: { zh: '概览 · 故事的结局', en: 'Overview · How the story ends' } },
    { id: 'deeper/05-kingdom-of-god', reason: { zh: '相关一课 · 已经和还没有', en: 'Related lesson · Already and not yet' } },
  ],
  'deeper/11-ancient-near-east': [
    { id: 'seeking/04-what-history-can-show', reason: { zh: '相关一课 · 考古能说明什么', en: 'Related lesson · What archaeology can show' } },
    { id: 'curious/10-out-of-egypt', reason: { zh: '概览 · 出埃及和西奈之约', en: 'Overview · The exodus and the Sinai covenant' } },
  ],
  'deeper/12-pauls-cities': [
    { id: 'curious/14-the-church-begins', reason: { zh: '概览 · 教会是怎样开始的', en: 'Overview · How the church began' } },
    { id: 'deeper/09-reading-the-letters', reason: { zh: '接着读 · 怎样读书信', en: 'Next · How to read the letters' } },
  ],
  'deeper/13-hard-moments-in-a-group': [
    { id: 'deeper/04-leading-a-study', reason: { zh: '相关一课 · 怎样带查经', en: 'Related lesson · How to lead a study' } },
    { id: 'new/07-doubt-and-temptation', reason: { zh: '相关一课 · 有疑惑的时候', en: 'Related lesson · When doubts come' } },
  ],
  'deeper/14-early-church-and-creeds': [
    { id: 'new/09-one-god-three-persons', reason: { zh: '相关一课 · 三位一体', en: 'Related lesson · The Trinity' } },
    { id: 'deeper/15-the-reformation', reason: { zh: '接着读 · 宗教改革', en: 'Next · The Reformation' } },
  ],
  'deeper/15-the-reformation': [
    { id: 'deeper/17-justification-and-sanctification', reason: { zh: '读深一点 · 称义和成圣', en: 'Going deeper · Justification and sanctification' } },
    { id: 'deeper/16-the-bible-in-chinese', reason: { zh: '接着读 · 中文圣经的历史', en: 'Next · The history of the Chinese Bible' } },
  ],
  'deeper/16-the-bible-in-chinese': [
    { id: 'curious/03-how-the-bible-came-to-us', reason: { zh: '概览 · 圣经是怎样传下来的', en: 'Overview · How the Bible came to us' } },
    { id: 'deeper/20-original-languages-and-tools', reason: { zh: '动手做 · 对照几个译本', en: 'Try it · Comparing translations' } },
  ],
  'deeper/17-justification-and-sanctification': [
    { id: 'seeking/12-grace', reason: { zh: '背景 · 恩典', en: 'Background · Grace' } },
    { id: 'new/06-when-i-fail', reason: { zh: '相关一课 · 犯了错怎么办', en: 'Related lesson · When you fail' } },
  ],
  'deeper/18-understanding-the-atonement': [
    { id: 'curious/12-why-the-cross', reason: { zh: '概览 · 耶稣为什么死在十字架上', en: 'Overview · Why Jesus died on a cross' } },
    { id: 'deeper/06-god-dwelling-with-people', reason: { zh: '相关一课 · 幔子裂开和神的同在', en: 'Related lesson · The torn veil and God’s presence' } },
  ],
  'deeper/19-sovereignty-and-choice': [
    { id: 'seeking/13-counting-the-cost', reason: { zh: '相关一课 · 跟随耶稣的选择', en: 'Related lesson · The choice to follow Jesus' } },
    { id: 'deeper/13-hard-moments-in-a-group', reason: { zh: '动手做 · 小组里讨论分歧', en: 'Try it · Discussing disagreements in a group' } },
  ],
  'deeper/20-original-languages-and-tools': [
    { id: 'curious/08-how-to-look-up-a-verse', reason: { zh: '入门 · 怎样查经文', en: 'First look · How to look up a passage' } },
    { id: 'deeper/04-leading-a-study', reason: { zh: '动手做 · 用工具书预备查经', en: 'Try it · Preparing a study with tools' } },
  ],
  'new/13-the-church-and-the-communion-of-saints': [
    { id: 'new/10-finding-a-church', reason: { zh: '动手做 · 找一间教会并扎根', en: "Try it · Finding a church and putting down roots" } },
    { id: 'deeper/14-early-church-and-creeds', reason: { zh: '读深一点 · 信经是怎样来的', en: "Going deeper · Where the creeds came from" } },
  ],
  'new/14-forgiveness-resurrection-and-life-everlasting': [
    { id: 'new/06-when-i-fail', reason: { zh: '相关一课 · 信主以后又犯错了怎么办', en: "Related lesson · When I fail after believing" } },
    { id: 'curious/15-new-heaven-new-earth', reason: { zh: '相关一课 · 新天新地', en: "Related lesson · The new heaven and new earth" } },
  ],
  'new/15-assurance': [
    { id: 'new/07-doubt-and-temptation', reason: { zh: '相关一课 · 有疑惑、受试探的时候', en: "Related lesson · When you doubt or are tempted" } },
    { id: 'deeper/19-sovereignty-and-choice', reason: { zh: '读深一点 · 神的主权和人的选择', en: "Going deeper · God's sovereignty and human choice" } },
  ],
  'new/16-forgiving-others': [
    { id: 'new/02-learning-to-pray', reason: { zh: '相关一课 · 主祷文里的“免我们的债”', en: "Related lesson · “Forgive us our debts” in the Lord's Prayer" } },
    { id: 'deeper/13-hard-moments-in-a-group', reason: { zh: '读深一点 · 小组里遇到难处', en: "Going deeper · Hard moments in a group" } },
  ],
  'new/17-money-and-giving': [
    { id: 'curious/07-what-jesus-taught', reason: { zh: '相关一课 · 登山宝训里的财宝和忧虑', en: "Related lesson · Treasure and worry in the Sermon on the Mount" } },
    { id: 'new/11-gifts-and-serving', reason: { zh: '接着读 · 恩赐和服事', en: "Next · Gifts and serving" } },
  ],
  'new/18-work-and-study': [
    { id: 'new/11-gifts-and-serving', reason: { zh: '相关一课 · 每个人都有用处', en: "Related lesson · Everyone has a part" } },
    { id: 'deeper/15-the-reformation', reason: { zh: '读深一点 · 宗教改革和“信徒皆祭司”', en: "Going deeper · The Reformation and the priesthood of all believers" } },
  ],
  'new/19-making-decisions': [
    { id: 'new/02-learning-to-pray', reason: { zh: '动手做 · 为这个决定祷告', en: "Try it · Pray about the decision" } },
    { id: 'deeper/19-sovereignty-and-choice', reason: { zh: '读深一点 · 神的主权和人的选择', en: "Going deeper · God's sovereignty and human choice" } },
  ],
  'new/20-when-suffering-comes': [
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '想查证 · 如果神良善，为什么有苦难', en: "Checking the evidence · If God is good, why is there suffering?" } },
    { id: 'deeper/07-reading-psalms-and-wisdom', reason: { zh: '读深一点 · 诗篇里的哀歌和约伯记', en: "Going deeper · Laments in the Psalms, and Job" } },
  ],
  'new/21-mark-1-who-is-this': [
    { id: 'curious/06-who-is-jesus', reason: { zh: '相关一课 · 耶稣是谁', en: "Related lesson · Who is Jesus?" } },
    { id: 'seeking/10-four-gospels', reason: { zh: '想查证 · 为什么有四本福音书', en: "Checking the evidence · Why four Gospels?" } },
  ],
  'new/22-mark-2-the-way-of-the-cross': [
    { id: 'seeking/13-counting-the-cost', reason: { zh: '相关一课 · 跟随耶稣意味着什么', en: "Related lesson · What following Jesus involves" } },
    { id: 'deeper/05-kingdom-of-god', reason: { zh: '读深一点 · 神的国', en: "Going deeper · The kingdom of God" } },
  ],
  'new/23-mark-3-jerusalem': [
    { id: 'deeper/06-god-dwelling-with-people', reason: { zh: '读深一点 · 圣殿主线', en: "Going deeper · The temple thread" } },
    { id: 'deeper/03-second-temple-world', reason: { zh: '读深一点 · 第二圣殿与罗马世界', en: "Going deeper · The Second Temple and Roman world" } },
  ],
  'new/24-mark-4-cross-and-empty-tomb': [
    { id: 'curious/12-why-the-cross', reason: { zh: '相关一课 · 耶稣为什么死在十字架上', en: "Related lesson · Why Jesus died on the cross" } },
    { id: 'seeking/09-did-jesus-rise', reason: { zh: '想查证 · 历史学家怎样看复活的证据', en: "Checking the evidence · How historians weigh the resurrection" } },
  ],
  'curious/16-the-birth-of-jesus': [
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '读深一点 · 信经怎样讲耶稣', en: "Going deeper · What the creed says about Jesus" } },
    { id: 'seeking/04-what-history-can-show', reason: { zh: '想查证 · 历史和考古能说明什么', en: "Checking the evidence · What history and archaeology can show" } },
  ],
  'curious/17-miracles-of-jesus': [
    { id: 'seeking/08-science-and-faith', reason: { zh: '想查证 · 科学和信仰一定冲突吗', en: "Checking the evidence · Must science and faith conflict?" } },
    { id: 'new/21-mark-1-who-is-this', reason: { zh: '动手做 · 读马可福音前八章', en: "Try it · Read Mark 1–8" } },
  ],
  'curious/18-people-jesus-met': [
    { id: 'seeking/06-what-it-means-to-believe', reason: { zh: '接着想 · “信”是什么意思', en: "Thinking further · What it means to believe" } },
    { id: 'seeking/12-grace', reason: { zh: '接着想 · 恩典', en: "Thinking further · Grace" } },
  ],
  'curious/19-the-lost-son': [
    { id: 'seeking/12-grace', reason: { zh: '接着想 · 为什么得救不能靠自己挣', en: "Thinking further · Why salvation can't be earned" } },
    { id: 'seeking/11-what-is-sin', reason: { zh: '接着想 · 圣经说的“罪”', en: "Thinking further · What the Bible means by sin" } },
  ],
  'curious/20-the-last-week': [
    { id: 'new/23-mark-3-jerusalem', reason: { zh: '动手做 · 读马可福音 11–13 章', en: "Try it · Read Mark 11–13" } },
    { id: 'deeper/18-understanding-the-atonement', reason: { zh: '读深一点 · 十字架成就了什么', en: "Going deeper · What the cross accomplished" } },
  ],
  'curious/21-david-and-the-psalms': [
    { id: 'deeper/07-reading-psalms-and-wisdom', reason: { zh: '读深一点 · 怎样读诗篇和智慧书', en: "Going deeper · Reading the Psalms and wisdom books" } },
    { id: 'deeper/01-covenant-thread', reason: { zh: '读深一点 · 圣约主线里的大卫之约', en: "Going deeper · The covenant with David in the covenant thread" } },
  ],
  'curious/22-feasts-of-israel': [
    { id: 'deeper/06-god-dwelling-with-people', reason: { zh: '读深一点 · 圣殿主线', en: "Going deeper · The temple thread" } },
    { id: 'new/05-baptism-and-communion', reason: { zh: '相关一课 · 圣餐和逾越节', en: "Related lesson · Communion and Passover" } },
  ],
  'curious/23-common-words': [
    { id: 'seeking/11-what-is-sin', reason: { zh: '接着想 · 圣经说的“罪”', en: "Thinking further · What the Bible means by sin" } },
    { id: 'seeking/06-what-it-means-to-believe', reason: { zh: '接着想 · “信”是什么意思', en: "Thinking further · What it means to believe" } },
  ],
  'seeking/14-old-testament-wars': [
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '相关一课 · 如果神良善，为什么有苦难', en: "Related lesson · If God is good, why is there suffering?" } },
    { id: 'deeper/11-ancient-near-east', reason: { zh: '读深一点 · 古代近东的背景', en: "Going deeper · The ancient Near East background" } },
  ],
  'seeking/15-wrongs-done-by-the-church': [
    { id: 'deeper/15-the-reformation', reason: { zh: '读深一点 · 宗教改革', en: "Going deeper · The Reformation" } },
    { id: 'seeking/11-what-is-sin', reason: { zh: '接着想 · 圣经说的“罪”', en: "Thinking further · What the Bible means by sin" } },
  ],
  'seeking/16-hell-and-judgment': [
    { id: 'deeper/18-understanding-the-atonement', reason: { zh: '读深一点 · 十字架成就了什么', en: "Going deeper · What the cross accomplished" } },
    { id: 'curious/15-new-heaven-new-earth', reason: { zh: '相关一课 · 新天新地', en: "Related lesson · The new heaven and new earth" } },
  ],
  'seeking/17-does-prayer-work': [
    { id: 'new/02-learning-to-pray', reason: { zh: '动手做 · 学习祷告', en: "Try it · Learning to pray" } },
    { id: 'new/20-when-suffering-comes', reason: { zh: '相关一课 · 受苦的时候', en: "Related lesson · When suffering comes" } },
  ],
  'seeking/18-will-i-lose-my-freedom': [
    { id: 'seeking/13-counting-the-cost', reason: { zh: '接着想 · 跟随耶稣的代价', en: "Thinking further · The cost of following Jesus" } },
    { id: 'seeking/12-grace', reason: { zh: '接着想 · 恩典', en: "Thinking further · Grace" } },
  ],
  'seeking/19-when-family-does-not-understand': [
    { id: 'new/16-forgiving-others', reason: { zh: '相关一课 · 饶恕和和好', en: "Related lesson · Forgiveness and reconciliation" } },
    { id: 'new/10-finding-a-church', reason: { zh: '动手做 · 找一间教会', en: "Try it · Finding a church" } },
  ],
  'seeking/20-the-bible-and-other-ancient-books': [
    { id: 'seeking/05-manuscripts', reason: { zh: '想查证 · 抄本和文本', en: "Checking the evidence · Manuscripts and the text" } },
    { id: 'seeking/07-are-all-religions-the-same', reason: { zh: '相关一课 · 所有宗教都一样吗', en: "Related lesson · Are all religions the same?" } },
  ],
  'seeking/21-how-do-i-become-a-christian': [
    { id: 'new/01-reading-every-day', reason: { zh: '下一步 · 每天读经', en: "Next step · Reading every day" } },
    { id: 'new/05-baptism-and-communion', reason: { zh: '下一步 · 洗礼和圣餐', en: "Next step · Baptism and communion" } },
  ],
};

const data: { tracks: TrackInfo[] } = JSON.parse(document.getElementById('app-data')?.textContent || '{"tracks":[]}');
const $$ = <T extends Element = HTMLElement>(sel: string, root: ParentNode = document) => Array.from(root.querySelectorAll<T & Element>(sel)) as T[];
const esc = (s = '') => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]!);
const ui = (zh: string, en: string) => `<span data-ui="zh">${esc(zh)}</span><span data-ui="en">${esc(en)}</span>`;
const bi = (t: Text) =>
  t.en ? `<span data-lang="zh" class="bi-zh">${esc(t.zh)}</span><span data-lang="en" class="bi-en">${esc(t.en)}</span>` : `<span data-lang="both">${esc(t.zh)}</span>`;
const trackById = (id?: string) => data.tracks.find((t) => t.id === id);
const doneIn = (t: TrackInfo, s: State) => t.lessons.filter((l) => s.completed[l.id]).length;
const nextIn = (t: TrackInfo, s: State) => t.lessons.find((l) => !s.completed[l.id]);

// ---------- toast ----------
let toastTimer: number | undefined;
function toast(zh: string, en: string) {
  const el = document.querySelector<HTMLElement>('[data-toast]');
  if (!el) return;
  el.innerHTML = ui(zh, en);
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => el.classList.remove('show'), 2600);
}

// ---------- settings ----------
const LANG_LABEL: Record<LangMode, string> = { zh: '中文', both: '中英', en: 'EN' };
function applySettings(s: State) {
  const d = document.documentElement;
  d.dataset.langMode = s.settings.lang;
  d.dataset.theme = s.settings.theme;
  d.dataset.size = s.settings.size;
  d.dataset.hasTrack = s.track ? 'yes' : 'no';
  if (s.track) d.dataset.track = s.track;
  else delete d.dataset.track;
  d.lang = s.settings.lang === 'en' ? 'en' : 'zh-Hans';
  $$('[data-lang-label]').forEach((el) => (el.textContent = LANG_LABEL[s.settings.lang]));
  $$('[data-set-lang]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.setLang === s.settings.lang)));
  $$('[data-set-theme]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.setTheme === s.settings.theme)));
  $$('[data-set-size]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.setSize === s.settings.size)));
}

document.addEventListener('click', (e) => {
  const target = e.target as HTMLElement;
  const lang = target.closest<HTMLElement>('[data-set-lang]');
  if (lang) store.update((s) => (s.settings.lang = lang.dataset.setLang as LangMode));
  if (target.closest('[data-cycle-lang]')) {
    const order: LangMode[] = ['zh', 'both', 'en'];
    store.update((s) => (s.settings.lang = order[(order.indexOf(s.settings.lang) + 1) % 3]));
  }
  const theme = target.closest<HTMLElement>('[data-set-theme]');
  if (theme) store.update((s) => (s.settings.theme = theme.dataset.setTheme as State['settings']['theme']));
  const size = target.closest<HTMLElement>('[data-set-size]');
  if (size) store.update((s) => (s.settings.size = size.dataset.setSize as State['settings']['size']));

  const choose = target.closest<HTMLElement>('[data-choose-track], [data-set-track]');
  if (choose) {
    const id = choose.dataset.chooseTrack || choose.dataset.setTrack!;
    store.update((s) => (s.track = id));
    if (choose.dataset.setTrack) toast('已设为我的路径', 'Set as my path');
  }
});

// ---------- progress everywhere ----------
function renderProgress(s: State) {
  for (const t of data.tracks) {
    const done = doneIn(t, s);
    const total = t.lessons.length;
    $$(`[data-track-progress="${t.id}"]`).forEach((ring) => {
      const fg = ring.querySelector<SVGCircleElement>('.ring-fg');
      const c = Number(fg?.dataset.circ || 0);
      fg?.setAttribute('stroke-dashoffset', String(total ? c * (1 - done / total) : c));
      const label = ring.querySelector('[data-ring-label]');
      if (label) label.textContent = `${done}/${total}`;
    });
    $$(`[data-track-count="${t.id}"]`).forEach((el) => (el.textContent = done ? `${done}/${total}` : ''));
    const next = nextIn(t, s);
    for (const u of t.units) {
      const ud = u.lessons.filter((id) => s.completed[id]).length;
      $$(`[data-unit-progress="${t.id}:${u.id}"]`).forEach((el) => {
        el.style.setProperty('--p', u.lessons.length ? String(ud / u.lessons.length) : '0');
        const label = el.querySelector('[data-unit-label]');
        if (label) label.textContent = `${ud}/${u.lessons.length}`;
      });
    }
    for (const l of t.lessons) {
      $$(`[data-lesson-node="${l.id}"]`).forEach((el) => {
        el.classList.toggle('done', Boolean(s.completed[l.id]));
        el.classList.toggle('current', next?.id === l.id);
      });
    }
  }
  const lessons = data.tracks.flatMap((x) => x.lessons).filter((l) => s.completed[l.id]);
  const noteKeys = Object.keys(s.notes || {}).filter((k) => s.notes[k]?.trim());
  const stat = (k: string, v: number) => $$(`[data-stat="${k}"]`).forEach((el) => (el.textContent = String(v)));
  stat('week', store.daysThisWeek(s));
  stat('done', lessons.length);
  stat('minutes', lessons.reduce((a, l) => a + l.minutes, 0));
  stat('notes', noteKeys.length);
  $$('[data-track-card]').forEach((el) => el.classList.toggle('is-mine', el.dataset.trackCard === s.track));
  $$('[data-set-track]').forEach((el) => el.toggleAttribute('hidden', el.dataset.setTrack === s.track));
  $$('[data-is-my-track]').forEach((el) => el.toggleAttribute('hidden', el.dataset.isMyTrack !== s.track));
  renderMyNotes(s);
}

function renderMyNotes(s: State) {
  const box = document.querySelector<HTMLElement>('[data-my-notes]');
  if (!box) return;
  const allLessons = data.tracks.flatMap((t) => t.lessons.map((l) => ({ track: t, lesson: l })));
  const entries = Object.entries(s.notes || {})
    .filter(([, text]) => text && text.trim())
    .map(([id, text]) => ({
      id,
      text: text.trim(),
      found: allLessons.find((x) => x.lesson.id === id),
    }));
  if (!entries.length) {
    box.innerHTML = `<div class="notes-empty">
      <p>${ui('还没有保存的思考笔记。', 'No reflection notes saved yet.')}</p>
      <p class="muted small">${ui('在任意一课的「想一想」下方写下你的体会，会自动保存在本机浏览器中，并随备份文件一起导出。', 'Write your thoughts under "Reflect" in any lesson. They stay in this browser and are included when you export a backup.')}</p>
    </div>`;
    return;
  }
  box.innerHTML = `<ul class="notes-list">${entries
    .map(({ id, text, found }) => {
      const title = found ? bi(found.lesson.title) : esc(id);
      const href = found ? found.lesson.url : '#';
      const trackBadge = found ? `<span class="note-track" style="--accent:${esc(found.track.color)}">${bi(found.track.title)}</span>` : '';
      return `<li class="note-card">
        <div class="note-head">
          <a class="note-lesson-link" href="${href}">${title}</a>
          ${trackBadge}
        </div>
        <p class="note-body">${esc(text)}</p>
      </li>`;
    })
    .join('')}</ul>`;
}

// ---------- home dashboard ----------
function renderHome(s: State) {
  const box = document.querySelector<HTMLElement>('[data-continue]');
  if (!box) return;
  const t = trackById(s.track);
  if (!t) return;
  const next = nextIn(t, s);
  const done = doneIn(t, s);
  document.documentElement.style.setProperty('--accent', t.color);
  $$('[data-home-track]').forEach((el) => (el.innerHTML = bi(t.title)));
  $$('[data-home-track-link]').forEach((el) => el.setAttribute('href', t.url));
  if (next) {
    const unit = t.units.find((u) => u.id === next.unit);
    box.innerHTML = `
      <p class="eyebrow">${done ? ui('继续学习', 'Continue') : ui('从这里开始', 'Start here')}</p>
      <h2 class="continue-title">${bi(next.title)}</h2>
      <p class="muted">${unit ? bi(unit.title) : ''} · ${ui(`约 ${next.minutes} 分钟`, `${next.minutes} min`)}</p>
      <a class="btn btn-primary" href="${next.url}">${done ? ui('继续', 'Continue') : ui('开始第一课', 'Start lesson 1')}</a>`;
  } else if (t.lessons.length) {
    box.innerHTML = `
      <p class="eyebrow">${ui('这条路径已完成', 'Path complete')}</p>
      <h2 class="continue-title">${ui('你已经读完了目前的所有课程', "You've finished every lesson so far")}</h2>
      <p class="muted">${ui('新课程会陆续加入。也可以看看下一条路径。', 'New lessons are on the way. Or explore the next path.')}</p>
      <a class="btn btn-primary" href="${t.url}">${ui('回顾这条路径', 'Review this path')}</a>`;
  }
  renderForYou(s, next?.id);
}

function renderForYou(s: State, primaryNextId?: string) {
  const wrap = document.querySelector<HTMLElement>('[data-for-you-wrap]');
  const grid = document.querySelector<HTMLElement>('[data-for-you]');
  if (!wrap || !grid) return;

  const all = data.tracks.flatMap((t) => t.lessons.map((l) => ({ track: t, lesson: l })));
  const byId = new Map(all.map((x) => [x.lesson.id, x]));

  const recentDoneId = Object.entries(s.completed || {})
    .sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0))
    .map(([id]) => id)[0];
  const anchorId = s.last || recentDoneId || primaryNextId;

  const picks: { track: TrackInfo; lesson: LessonInfo; reason: Text }[] = [];
  const seen = new Set<string>();
  if (primaryNextId) seen.add(primaryNextId);

  const pushPick = (id: string, reason: Text) => {
    if (picks.length >= 3 || seen.has(id) || s.completed[id]) return;
    const found = byId.get(id);
    if (!found) return;
    seen.add(id);
    picks.push({ ...found, reason });
  };

  if (anchorId && RELATED_BRIDGES[anchorId]) {
    for (const b of RELATED_BRIDGES[anchorId]) pushPick(b.id, b.reason);
  }
  if (recentDoneId && recentDoneId !== anchorId && RELATED_BRIDGES[recentDoneId]) {
    for (const b of RELATED_BRIDGES[recentDoneId]) pushPick(b.id, b.reason);
  }

  for (const t of data.tracks) {
    if (t.id === s.track) continue;
    const cand = nextIn(t, s);
    if (cand) {
      pushPick(cand.id, {
        zh: `另一条路径 · ${t.title.zh}`,
        en: `Another path · ${t.title.en || t.title.zh}`,
      });
    }
  }

  if (!picks.length) {
    wrap.setAttribute('hidden', '');
    return;
  }
  wrap.removeAttribute('hidden');
  grid.innerHTML = picks
    .map(
      ({ track, lesson, reason }) => `
      <a class="question-card" href="${lesson.url}">
        <span class="question-tag">${bi(reason)}</span>
        <strong class="question-title">${bi(lesson.title)}</strong>
        <p class="muted small">${bi(lesson.summary)}</p>
        <span class="question-cta">${bi(track.title)} · ${ui(`约 ${lesson.minutes} 分钟`, `${lesson.minutes} min`)}</span>
      </a>`,
    )
    .join('');
}

// ---------- lesson page ----------
function setupLesson() {
  const article = document.querySelector<HTMLElement>('[data-lesson-id]');
  if (!article) return;
  const id = article.dataset.lessonId!;
  if (store.get().last !== id) store.update((s) => (s.last = id));
  const btn = document.querySelector<HTMLButtonElement>('[data-complete]');
  const after = document.querySelector<HTMLElement>('[data-after-complete]');
  const noteInput = document.querySelector<HTMLTextAreaElement>('[data-lesson-note]');
  const noteStatus = document.querySelector<HTMLElement>('[data-note-saved]');
  if (noteInput) {
    noteInput.value = store.get().notes?.[id] || '';
    let noteTimer: number | undefined;
    noteInput.addEventListener('input', () => {
      clearTimeout(noteTimer);
      noteTimer = window.setTimeout(() => {
        store.setNote(id, noteInput.value);
        if (noteStatus) {
          noteStatus.removeAttribute('hidden');
          window.setTimeout(() => noteStatus.setAttribute('hidden', ''), 1800);
        }
      }, 250);
    });
  }
  const paint = (s: State) => {
    const done = Boolean(s.completed[id]);
    btn?.classList.toggle('is-done', done);
    btn?.setAttribute('aria-pressed', String(done));
    after?.toggleAttribute('hidden', !done);
    if (noteInput && document.activeElement !== noteInput) {
      noteInput.value = s.notes?.[id] || '';
    }
  };
  btn?.addEventListener('click', () => {
    const done = !store.get().completed[id];
    store.setComplete(id, done);
    if (done) {
      toast('完成了！做得好', 'Lesson complete. Well done.');
      after?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  });
  store.subscribe(paint);
  paint(store.get());
}

// ---------- quick check ----------
function setupQuizzes() {
  $$('[data-quiz]').forEach((quiz) => {
    const answer = Number(quiz.dataset.answer);
    const options = $$<HTMLButtonElement>('[data-option]', quiz);
    options.forEach((opt) =>
      opt.addEventListener('click', () => {
        const right = Number(opt.dataset.option) === answer;
        options.forEach((o) => {
          o.disabled = true;
          if (Number(o.dataset.option) === answer) o.classList.add('correct');
        });
        if (!right) opt.classList.add('wrong');
        quiz.classList.add(right ? 'answered-right' : 'answered-wrong');
        quiz.querySelector('[data-quiz-result]')?.removeAttribute('hidden');
      }),
    );
  });
}

// ---------- me page ----------
function setupMe() {
  document.querySelector('[data-export]')?.addEventListener('click', () => {
    const blob = new Blob([store.exportJson()], { type: 'application/json' });
    const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: `covenant-learn-${store.today()}.json` });
    a.click();
    URL.revokeObjectURL(a.href);
  });
  document.querySelector<HTMLInputElement>('[data-import]')?.addEventListener('change', async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    try {
      store.importJson(await file.text());
      toast('已恢复学习记录', 'Progress restored');
    } catch {
      toast('这不是有效的备份文件', 'That is not a valid backup file');
    }
  });
  const reset = document.querySelector<HTMLButtonElement>('[data-reset]');
  reset?.addEventListener('click', () => {
    if (reset.dataset.armed) {
      store.reset();
      delete reset.dataset.armed;
      reset.classList.remove('armed');
      toast('学习记录已清除', 'Progress cleared');
    } else {
      reset.dataset.armed = '1';
      reset.classList.add('armed');
      setTimeout(() => (delete reset.dataset.armed, reset.classList.remove('armed')), 4000);
    }
  });
}

function setupKeyboard() {
  document.addEventListener('keydown', (e) => {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey) return;
    const target = e.target as HTMLElement | null;
    if (target && (target.matches('input, textarea, select') || target.isContentEditable)) {
      if (e.key === 'Escape') target.blur();
      return;
    }
    if (e.key === 'l' || e.key === 'L') {
      const order: LangMode[] = ['zh', 'both', 'en'];
      let nextLang: LangMode = 'zh';
      store.update((s) => {
        nextLang = order[(order.indexOf(s.settings.lang) + 1) % 3];
        s.settings.lang = nextLang;
      });
      const msg: Record<LangMode, [string, string]> = {
        zh: ['显示语言：中文', 'Language: Chinese'],
        both: ['显示语言：中英对照', 'Language: Bilingual'],
        en: ['显示语言：English', 'Language: English'],
      };
      toast(msg[nextLang][0], msg[nextLang][1]);
    } else if (e.key === 'ArrowLeft' || e.key === '[') {
      const prev = document.querySelector<HTMLAnchorElement>('[data-prev-lesson]');
      if (prev) window.location.href = prev.href;
    } else if (e.key === 'ArrowRight' || e.key === ']') {
      const next = document.querySelector<HTMLAnchorElement>('[data-next-lesson]');
      if (next) window.location.href = next.href;
    } else if (e.key === 'n' || e.key === 'N') {
      const note = document.querySelector<HTMLTextAreaElement>('[data-lesson-note]');
      if (note) {
        e.preventDefault();
        note.focus();
        note.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else if (e.key === 'c' || e.key === 'C') {
      const btn = document.querySelector<HTMLButtonElement>('[data-complete]');
      if (btn) btn.click();
    }
  });
}

function renderAll(s: State) {
  applySettings(s);
  renderProgress(s);
  renderHome(s);
}

store.subscribe(renderAll);
renderAll(store.get());
setupLesson();
setupQuizzes();
setupMe();
setupKeyboard();

// Keep tabs in sync if progress changes in another tab/window.
window.addEventListener('storage', (e) => {
  if (e.key === store.KEY) store.refresh();
});
