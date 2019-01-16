/// P1_Test 线程任务， 支持8个刷机线程同时运行
func mainThread(){
    
    // 开一条全局队列异步执行任务
    DispatchQueue.global().async {
        
        /*  Group的用法
         *  1. notify(依赖任务), 必须和 enter/leave在同一队列才会执行
         *  2. wait(任务等待)
         *  3. enter/leave 手动管理group计数,enter和leave必须配对, 可以不需要wait()
         */
        let group = DispatchGroup()
        var subTask: [DispatchQueue] = [DispatchQueue]()
        
        /* // 主线程
         DispatchQueue.main.async {  //通知ui刷新
         print("Main 刷新 UI: Begin")
         group.wait()
         Thread.sleep(forTimeInterval: 1)   //停止1秒
         print("Main 刷新 UI: End")
         }   // */
        
        //初始化8个子线程
        for i in 0...7{
            subTask.append(DispatchQueue(label: "subTask\(i)", attributes: .concurrent))
        }
        //启动8个子线程任务
        for item in subTask{
            group.enter()   //把该任务添加到组队列中执行, enter和leave必须配对
            item.async(group: group) {
                Thread.sleep(forTimeInterval: 1)   //停止1秒
                print("\(Date().description) subTask.label = \(item.label)")
                DispatchQueue.main.async(group: group, execute: refreshMainUI(dq: item))     // 通知主线程刷新UI
                group.leave()   //执行完之后从组队列中移除
            }
            group.notify(queue: item){ // 对应的子线程完成后，扫尾任务
                    print("\(item.label) finished，do something more")
                    // *** 此处可添加 对应的子线程完成后的扫尾任务
                    sleep(10)
            }
        }
        print("Waitting all test done.")
        group.wait()    // 等待所有子线程完成
        print("All test done.")
    }
    
    // 通知主线程刷新UI, 有需要在主线程中执行的代码，请添加到此
    func refreshMainUI(dq:DispatchQueue) -> DispatchWorkItem{
        let workItem = DispatchWorkItem {
            print("Refresh main UI: \(dq.label): Hello world! ")
            // *** 此处可添加 UI 刷新任务
          //  Thread.sleep(forTimeInterval: 5)   //停止1秒
        }
        return workItem
    }
}