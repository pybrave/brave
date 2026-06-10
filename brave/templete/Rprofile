if (Sys.getenv("R_USER_WORKDIR")!= "") {
    print(paste0("setwd: ",Sys.getenv("R_USER_WORKDIR")))
    setwd(Sys.getenv("R_USER_WORKDIR"))
    # setwd()
    if (rstudioapi::isAvailable()) {
        rstudioapi::filesPaneNavigate(getwd())
        rstudioapi::navigateToFile(Sys.getenv("R_SCRIPT"))
    # later::later(function() {
    #     rstudioapi::filesPaneNavigate(getwd())
    #     print(paste0("rstudioapi::filesPaneNavigate: ",getwd()))
    #   }, delay = 3)  # 0.5秒后执行
    }
}
setHook("rstudio.sessionInit", function(newSession) {
    if (newSession){
        print(paste0("filesPaneNavigate: ",getwd()))
        rstudioapi::filesPaneNavigate(getwd())
        r_script = Sys.getenv("R_SCRIPT")
        print(paste0("navigateToFile: ",r_script))
        rstudioapi::navigateToFile(r_script)
    }
    if (interactive() && rstudioapi::isAvailable()) {
        rstudioapi::applyTheme("Tomorrow Night")
    }
        # rstudioapi::filesPaneNavigate(getwd())
}, action = "append")



# init <- function(){
#     if (rstudioapi::isAvailable()) {
        
        # print(paste0("filesPaneNavigate: ",getwd()))
        # rstudioapi::filesPaneNavigate(getwd())
        # r_script = Sys.getenv("R_SCRIPT")
        # print(paste0("navigateToFile: ",r_script))
        # rstudioapi::navigateToFile(r_script)
#     # later::later(function() {
#     #     rstudioapi::filesPaneNavigate(getwd())
#     #     print(paste0("rstudioapi::filesPaneNavigate: ",getwd()))
#     #   }, delay = 3)  # 0.5秒后执行
#     }
# }