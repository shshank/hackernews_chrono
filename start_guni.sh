for pid in `ps -ef| grep python|grep gunicorn|grep guni_conf| awk '{print $2}'`
    do
        kill -9 $pid
    done
gunicorn -c configs/guni_conf.py run:app