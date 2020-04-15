var status = 0; // 0:停止中 1:動作中
var time = 0;
var startBtn = document.getElementById("startBtn");
var timerLabel = document.getElementById('timerLabel');

// STARTボタン
function start(){
    // 動作中にする
    status = 1;
    // スタートボタンを押せないようにする
    startBtn.disabled = true;

    timer();
}

// STOPボタン
function stop(){
    // 停止中にする
    status = 0;
    // スタートボタンを押せるようにする
    startBtn.disabled = false;
}

// RESETボタン
function reset(){
    // 停止中にする
    status = 0;
    // タイムを0に戻す
    time = 0;
    // タイマーラベルをリセット
    timerLabel.innerHTML = '00:00';
    // スタートボタンを押せるようにする
    startBtn.disabled = false;
}

function timer(){
    // ステータスが動作中の場合のみ実行
    if (status == 1) {
        setTimeout(function() {
            time++;

            // 時・分・秒・ミリ秒を計算
            var hour = Math.floor(time/100/60/60);
            var min = Math.floor(time/100/60);
            var sec = Math.floor(time/100);
            var mSec = time % 100;

            // 時が1桁の場合は、先頭に0をつける
            if (hour < 10) hour = "0" + hour;

            // 分が60秒以上の場合 例）89分→29分にする
            if (min >= 60) min = min % 60;

            // 分が1桁の場合は、先頭に0をつける
            if (min < 10) min = "0" + min;

            // 秒が60秒以上の場合　例）89秒→29秒にする
            if (sec >= 60) sec = sec % 60;

            // 秒が1桁の場合は、先頭に0をつける
            if (sec < 10) sec = "0" + sec;

            // ミリ秒が1桁の場合は、先頭に0をつける
            if (mSec < 10) mSec = "0" + mSec;

            // タイマーラベルを更新
            timerLabel.innerHTML = hour + ":" + min;

            // 再びtimer()を呼び出す
            timer();
        }, 10);
    }
}