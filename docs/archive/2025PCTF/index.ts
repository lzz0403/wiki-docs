import { ElMessage } from "element-plus";

export function training() {
  window.open("https://gz.imxbt.cn/games/33/challenges");
}

export function signup() {
  const nowdate = new Date();
  const signdate = [new Date("2025-11-16 9:00:00"), new Date("2025-11-16 22:00:00")];
  if (nowdate.getTime() < signdate[0].getTime()) {
    ElMessage({
      message: "公开赛道报名通道于 11.16 9:00 开放",
      type: "warning",
    });
  } else if (nowdate.getTime() > signdate[1].getTime()) {
    ElMessage({
      message: "报名已结束！",
      type: "warning",
    });
  } else {
    const year = signdate[0].getFullYear();
    const matchname = "pctf";
    const origin = "play.pctf.top";
    const protocol = "https:";
    const path = `/${year}${matchname}`;
    window.open(`${protocol}//${origin}${path}`);
  }
}

export function participate(channel: "internal" | "external") {
  const time = {
    internal: [new Date("2025-11-1 09:00:00").getTime(), new Date("2025-11-30 21:00:00").getTime()],
    external: [new Date("2025-11-16 09:00:00").getTime(), new Date("2025-11-16 22:00:00").getTime()],
  };
  const now = Date.now();
  const gap = time[channel];
  if (!gap) return;
  if (now < gap[0]) {
    ElMessage({
      message: "比赛尚未开始！",
      type: "warning",
    });
  } else if (now > gap[1]) {
    ElMessage({
      message: "比赛已结束！",
      type: "warning",
    });
  } else {
    const year = new Date(gap[0]).getFullYear();
    const matchname = "pctf";
    const origin = "play.pctf.top";
    const protocol = "https:";
    const tail = {
      internal: "xn",
      external: "gk",
    }[channel];
    const path = `/${year}${matchname}${tail}`;
    window.open(`${protocol}//${origin}${path}`);
  }
}
