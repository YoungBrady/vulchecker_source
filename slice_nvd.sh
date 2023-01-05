#!/bin/bash
# set -x
# $1 software $2 c/s  c=count s=slice
startTime=`date +"%Y-%m-%d %H:%M:%S"`

# source /etc/profile
neo4j_path=/opt/neo4j-community-2.1.8/bin
joern_path=/opt/joern-0.3.1
batch=$1
slice_root=/home/lyl/huawei_project
code_path=$slice_root/code

data_path=$slice_root/NVD
if [[ $2 == 's' ]];then

  for cwe in $(ls $data_path)
  do
    for cve in $(ls $data_path/$cwe/merge/$batch)
    do
      if [[ $cve != 'ffmpegCVE-2011-3929' ]];then
        continue
      fi
      for type in {'old','new'}
      do
          # if [[ $type == 'new' ]];then
          # continue
          # fi
          data_batch="$data_path/$cwe/merge/$batch/$cve/$type" # 源代码路径
          
          batch_dir="$slice_root/slice_all/NVD/$cwe/$batch/$cve/$type" # 存放切片结果
          echo $batch_dir
          output_path="$batch_dir/logs/output.txt"
          error_path="$batch_dir/logs/error.txt"


          cd $slice_root
          if [[ ! -d $batch_dir ]];then
            mkdir -p  $batch_dir
            echo "mkdir batch_dir complete"
          fi

          cd $code_path
          cp sensitive_func.pkl $batch_dir
          cd $batch_dir
          if [[ -d "logs" ]];then
            rm -rf logs
            echo "del logs complete!"
          fi
          mkdir logs
          output_path="$batch_dir/logs/output.txt"
          error_path="$batch_dir/logs/error.txt"
          # break
          cd $neo4j_path
          sudo ./neo4j stop
          sleep 5
          status=`./neo4j status`
          if [[ "$status"x == "Neo4j Server is not running"x ]];then
            echo "neo4j stop completed!"
          else
            echo "neo4j stop failed!" >> $error_path
            continue
          fi

          cd $joern_path
          if [[ -d ".joernIndex" ]];then
            rm -rf .joernIndex
            echo "del joernIndex complete!"
          fi
          if [[ -d "$data_batch" ]];then
            # ./joern $data_path 2>> $error_path
            java -Xmx32g -jar ./bin/joern.jar $data_batch
            echo "joern parse complete!"
          else
            echo "$data_batch does not exist!" >> $error_path
            continue
          fi
          # if [[ ! -s $error_path ]];then
          #   echo "joern analysis completed!"
          # else
          #   echo "joern analysis failed!" >> $output_path
          #   exit 1
          # fi
          cd $neo4j_path
          sudo ./neo4j start-no-wait
          sleep 20
          status=`./neo4j status`
          if [[ "${status:0:30}"x == "Neo4j Server is running at pid"x ]];then
            echo "neo4j start completed!"
          else
            echo "neo4j start failed" >> $output_path
            continue
          fi
          ./neo4j status
          cd $batch_dir
          if [[ -d "cfg_db" ]];then
            rm -rf cfg_db
            echo "del cfg_db complete!"
          fi
          # mkdir "cfg_db"
          if [[ -d "pdg_db" ]];then
            rm -rf pdg_db
            echo "del pdg_db complete!"
          fi
          # mkdir "pdg_db"
          if [[ -d "dict_call2cfgNodeID_funcID" ]];then
            rm -rf dict_call2cfgNodeID_funcID
            echo "del dict complete!"
          fi
          # mkdir "dict_call2cfgNodeID_funcID"
          if [[ -d "silce_source" ]];then
            rm -rf "silce_source"
            echo "del slice_source complete!"
          fi

          if [[ -d "edges_source" ]];then
            rm -rf "edges_source"
            echo "del edges_source complete!"
          fi

          sudo python2 $code_path/get_cfg_relation.py 2>> $error_path
          if [[ ! -s $error_path ]];then
            echo "build cfg completed!"
          else
            echo "build cfg failed!" >> $output_path
            continue
          fi
          sudo python2 $code_path/complete_PDG.py 2>> $error_path
          if [[ ! -s $error_path ]];then
            echo "build pdg completed!"
          else
            echo "build pdg failed!" >> $output_path
            continue
          fi

          # if [[ ! -s $output_path ]];then
          #   echo "generate PDG success" >> $output_path
          # else
          #   echo $data_batch"something wrong" >> $output_path
          #   continue
          # fi

          sudo python2 $code_path/access_db_operate.py 2>> $error_path
          if [[ ! -s $error_path ]];then
            echo "build dict completed!"
          else
            echo "build dict failed!" >> $output_path
            continue
          fi
          sudo python2 $code_path/get_points.py $data_batch NVD $type 2>> $error_path
          if [[ ! -s $error_path ]];then
            echo "get points completed!"
          else
            echo "get points failed!" >> $output_path
            continue
          fi
          sudo python2 $code_path/get_slices.py 2>> $error_path
          if [[ ! -s $error_path ]];then
            echo "get slice completed!"
          else
            echo $data_batch"get slice failed!" >> $output_path
            continue
          fi
          python3 $code_path/draw_slice.py $type 2>> $error_path
          if [[ ! -s $error_path ]];then
            echo "draw slice completed!"
          else
            echo $data_batch"draw slice failed!" >> $output_path
            continue
          fi
      done
    done
  done

else

  for cwe in $(ls $data_path)
  do
    i=0
    j=0
    for cve in $(ls $data_path/$cwe/merge/$batch)
    do
      # if [[ $cve != 'binutilsCVE-2017-14129' ]];then
      #   continue
      # fi
      for type in {'old','new'}
      do
          data_batch="$data_path/$cwe/merge/$batch/$cve/$type" # 源代码路径
          
          batch_dir="$slice_root/slice_all/NVD/$cwe/$batch/$cve/$type" # 存放切片结果
          # echo $batch_dir
          output_path="$batch_dir/logs/output.txt"
          error_path="$batch_dir/logs/error.txt"
          if [[ -e $output_path ]];then
              ((j++))
              echo $batch_dir
          else
              ((i++))
          fi
      done
    done
    echo $cwe $i complete $j remain
  done
fi




endTime=`date +"%Y-%m-%d %H:%M:%S"`
st=`date -d  "$startTime" +%s`
et=`date -d  "$endTime" +%s`
sumTime=$(($et-$st))
echo "Total time is : $sumTime second."