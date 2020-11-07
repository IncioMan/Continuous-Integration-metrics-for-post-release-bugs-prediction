echo "Starting.."
until python3 data_retrivers/log_retriever.py 
do
    echo "Log retriever crashed with exit code $?.  Respawning.." >&2
    sleep 1
done