
const { createApp } = Vue;


const treeNode = {
  name: 'tree-node',
  props: {
    node: {
      type: Object,
      default: []
    }
  },
  template: `
    <div class="w-full pb-[4px]">
      <div class="node" @click.stop="toggle(node)">
          <div v-if="node.folderFlag" @click.stop="toggle(node)" :style="{backgroundColor:selectId === node.uuid?'#E4EFFF':''}" class="h-32px flex items-center cursor-pointer rounded-[6px] hover:bg-[#E4EFFF]">
            <i v-if="isExpanded" style="margin-left:4px" class="mr-10px fas fa-caret-down arrow"></i>
            <i v-else style="margin-left:4px" class="mr-10px fas fa-caret-right arrow"></i>
            <img
              src="./assets/img/pagelist-fold.png"
              type="icon-yemian"
              class="mr-3px"
            />
            <span class="text-[12px]" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" :title="node.name">{{ node.name }}</span>

          </div>
          <div v-else class="children ml-4 rounded-[6px] hover:bg-[#E4EFFF]" @click.stop="selectPage(node)" :style="{backgroundColor:selectId === node.uuid?'#E4EFFF':''}">
            <div class="">
              <div class="h-32px ml-10px flex items-center cursor-pointer">
                <img
                    v-if="node.pageScene === 'web'"
                    src="./assets/img/pagelist-web-page.png"
                    type="icon-yemian" 
                    class="mr-3px"
                  />
                  <img
                    v-else-if="node.pageScene === 'app'"
                    src="./assets/img/pagelist-app-page.png"
                    type="icon-yemian" 
                     class="mr-3px"
                  />
                  <img v-else class="mr-10px" src="./public/assets/preview/page.png" alt="">
                  <span class="text-[12px]" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" :title="node.pageName">{{ node.pageName }}</span>
              </div>
            </div>
          </div>
      </div>
      <ul v-show="isExpanded && node.folderFlag" class="pl-6">
        <li v-for="child in node.childrenList" :key="child.id">
          <tree-node :node="child" :selectId="selectId" @node-click="(event) => $emit('node-click', event)"></tree-node>
        </li>
      </ul>
    </div>
  `,
  data() {
    return {
      isExpanded: true
    }
  },
  inject: ['getSelectId'],
  computed: {
    selectId () {
      return this.getSelectId()
    },
  },
  methods: {
    toggle(node) {
      this.isExpanded = !this.isExpanded
      this.$emit('node-click', node)
    },
    selectPage(node){
      this.$emit('node-click', node)
    }
  }
}

const app = createApp({
  provide () {
    return {
      getSelectId: () => this.pageUuid
    }
  },
  data() {
    return {
      message: 'Hello Vue!',
      treeData: [],
      appVersion: '',
      pageUuid: '',
      pageType:'',
      pageName: '',
      previewSizeOptions: [],
      previewSizeW: 1920,
      previewSizeH: 1080,
      previewSize: '1920x1080',
      cleanup: null,
      currentIndex: 0,
      pageList: [],
      isPreview: false,
      isShowTip: false,
      appName: projectName,
      resizeObserver: null,
      setTimeout1: null,
      isHtml: true,
      url: '',
      childUrl: '',
      iframeMessage: null,
      childIframe: null, // 导航页内嵌子页面添加键盘事件
      drag: null
    }
  },
  watch: {
    pageType:{
      handler(value){
        this.$nextTick(()=>{
          if (!this.appName) return
          this.changePageType(value)
          let iframeDoc = null
          let iframeAppDoc = null
          const iframeKeydownHandler=(e) => {
            this.keyboardEvents(e)
          }
          if (value === 'app') {
            if (iframeDoc) {
              iframeDoc.removeEventListener('keydown', iframeKeydownHandler);
            }
            const iframeId = this.isHtml ? '#iframeApp' : '#vueIframeApp'
            const iframeApp = document.querySelector(iframeId);
            // 聚焦到iframe时，键盘左右切换不生效 
            // iframeApp.addEventListener('load', () => {
            //   iframeAppDoc = iframeApp.contentDocument || iframeApp.contentWindow.document;
            //   iframeAppDoc.addEventListener('keydown', iframeKeydownHandler);
            //   if (!this.isHtml) {
            //     const tag = iframeAppDoc.querySelector('.ai-tag')
            //     tag && (tag.style && (tag.style.visibility = 'hidden') || tag.style.setAtrrbute('visibility','hidden'))
            //   }
            // });
            if (this.resizeObserver) {
              this.resizeObserver.disconnect()
              this.resizeObserver = null
            }
          } else {
            // 监听web类型iframe父元素大小变化
            const element = document.querySelector('.preview-web')
            this.resizeObserver = new ResizeObserver(entries => {
              for (let entry of entries) {
                const { width, height } = entry.contentRect
                if (this.previewSize == 'auto') {
                  this.previewSizeW = parseInt(width)
                  this.previewSizeH = parseInt(height)
                }
                this.changeResolution()
              }
            })
            this.resizeObserver.observe(element)
  
            if (iframeAppDoc) {
              iframeAppDoc.removeEventListener('keydown', iframeKeydownHandler);
            }
            // 聚焦到iframe时，键盘左右切换不生效 
            const iframeWeb = this.isHtml ? document.getElementById('iframe') :  document.getElementById('vueIframeWeb')
            iframeWeb.addEventListener('load', () => {
              iframeDoc = iframeWeb.contentDocument || iframeWeb.contentWindow.document;
              iframeDoc.addEventListener('keydown', iframeKeydownHandler);
            });
          }
        })
      }
    },
    isHtml(value){
      this.$nextTick(()=>{
        if (!this.appName) return
        let iframeDoc = null
        let iframeAppDoc = null
        const iframeKeydownHandler=(e) => {
          this.keyboardEvents(e)
        }
        if (value === 'app') {
          if (iframeDoc) {
            iframeDoc.removeEventListener('keydown', iframeKeydownHandler);
          }
          const iframeId = this.isHtml ? '#iframeApp' : '#vueIframeApp'
          const iframeApp = document.querySelector(iframeId);
          // 聚焦到iframe时，键盘左右切换不生效 
          // iframeApp.addEventListener('load', () => {
          //   iframeAppDoc = iframeApp.contentDocument || iframeApp.contentWindow.document;
          //   iframeAppDoc.addEventListener('keydown', iframeKeydownHandler);
          //   if (!this.isHtml) {
          //     this.$nextTick(() => {
          //       const tag = iframeAppDoc.querySelector('.ai-tag')
          //       tag && (tag.style && (tag.style.visibility = 'hidden') || tag.style.setAtrrbute('visibility','hidden'))
          //     })
          //   }
          // });
          if (this.resizeObserver) {
            this.resizeObserver.disconnect()
            this.resizeObserver = null
          }
        } else {
          // 监听web类型iframe父元素大小变化
          const element = document.querySelector('.preview-web')
          this.resizeObserver = new ResizeObserver(entries => {
            for (let entry of entries) {
              const { width, height } = entry.contentRect
              if (this.previewSize == 'auto') {
                this.previewSizeW = parseInt(width)
                this.previewSizeH = parseInt(height)
              }
              this.changeResolution()
            }
          })
          this.resizeObserver.observe(element)

          if (iframeAppDoc) {
            iframeAppDoc.removeEventListener('keydown', iframeKeydownHandler);
          }
          // 聚焦到iframe时，键盘左右切换不生效 
          const iframeWeb = this.isHtml ? document.getElementById('iframe') :  document.getElementById('vueIframeWeb')
          iframeWeb.addEventListener('load', () => {
            iframeDoc = iframeWeb.contentDocument || iframeWeb.contentWindow.document;
            iframeDoc.addEventListener('keydown', iframeKeydownHandler);
          });
        }
      })
    },
    previewSize(val) {
      const option = this.previewSizeOptions.find(item => item.value === val)
      this.previewSizeW = option.w
      this.previewSizeH= option.h
      this.changeResolution()
    },
    previewSizeW(val) {
      if (!this.appName) return
      this.changeResolution()
    },
    previewSizeH(val) {
      if (!this.appName) return
      this.changeResolution()
    }
  },
  mounted() {
    if (this.drag) {
      this.drag.destroy()
    }
    this.drag = new DraggableResizableModal();
    document.querySelector('#app').style.display = 'block'
    this.getPageList()
    this.communicationFun()
  },
  methods: {
    showDoc () {
      if (this.drag) {
        this.drag.show(this.appuuid, this.pageUuid)
      }
    },
    communicationFun () {
      this.iframeMessage = useEventListener(window, 'message', async (event) => {
        // 处理消息 判断data值是页面id时处理切换页面
        if (event.source != window) {
          const currentPage = this.pageList.find(item => item.pageUuid == event.data)
          this.pageUuid = currentPage.pageUuid
          this.pageName = currentPage.pageName
          this.pageType = currentPage.pageScene
          this.isHtml = currentPage.codeType.toLowerCase().includes('html')
          this.getAppPageVersion(currentPage)
          this.currentIndex = this.pageList.findIndex(item=>item.pageUuid == this.pageUuid) || 0;
        }
      }, true)
    },
    // 修改页面类型
    changePageType(value) {
      const autoSize = {
        label: "自定义",
        value: "auto",
        w: 375,
        h: 812
      }
      if (value === 'app') {
        this.previewSizeOptions = [autoSize, ...resolutionInfo.app]
        this.previewSizeW = 393
        this.previewSizeH= 852
        this.previewSize = '393x852-16'
      } else {
        let iframe = document.querySelector('.preview-web')
        autoSize.w = parseInt(iframe.clientWidth)
        autoSize.h = parseInt(iframe.clientHeight)
        this.previewSizeOptions = [autoSize, ...resolutionInfo.web]
        this.previewSizeW = autoSize.w
        this.previewSizeH= autoSize.h
        this.previewSize = 'auto'
      }
      this.changeResolution()
    },
    // 找第一个页面
    findFirstPage(treeData) {
      const queue = [...treeData];
      while (queue.length > 0) {
        const item = queue.shift();
        
        // 如果是有效页面，直接返回
        if (item.folderFlag === false && item.uuid) {
          return item;
        }
        
        // 如果是文件夹且有子节点，将子节点加入队列前端（优先处理）
        if (item.folderFlag === true && item.childrenList?.length) {
          queue.unshift(...item.childrenList);
        }
        
        // 如果是空文件夹，自动跳过（继续循环）
      }
      
      return null;
    },
    // 页面列表
    getPageList() {
      this.treeData = filterByHasVersion(treeArr)
      // const currentPage = this.treeData.find(item => item.default) || this.treeData[0]
      const currentPage = this.findFirstPage(this.treeData)
      console.log(this.treeData, this.pageList);
      
      this.pageUuid = currentPage.pageUuid
      this.pageName = currentPage.pageName
      this.pageType = currentPage.pageScene
      this.isHtml = currentPage.codeType.toLowerCase().includes('html')
      this.$nextTick(()=>{
        this.getAppPageVersion(currentPage)
      })
      collectItems(this.treeData, this.pageList);
      this.currentIndex = this.pageList.findIndex(item=>item.pageUuid == this.pageUuid) || 0;
      this.cleanup = this.createKeyboardNavigation();
    },
    // 获取应用中页面内容
    async getAppPageVersion(info) {
      const isApp = this.pageType == 'app'
      let iframe = this.isHtml ? document.getElementById('iframe') :  document.getElementById('vueIframeWeb')

      if (isApp) {
        iframe = document.getElementById('iframeApp')
      }
      if (info.parentUrl) {
        iframe.src = info.parentUrl
        this.childUrl = info.url
      } else {
        iframe.src = info.url;
      }
    },
    loadHtmlIframe() {
      if (this.childIframe) {
        this.childIframe()
        this.childIframe = null
      }
      const isApp = this.pageType == 'app'
      // let template = handleCode(this.pageHtml, !isApp);
      let iframe = document.getElementById('iframe')
      if (isApp) {
        iframe = document.getElementById('iframeApp')
      }
      const htmlIframe = iframe.contentDocument || iframe.contentWindow.document;
      if (htmlIframe) {
        const navIframe = htmlIframe.getElementById('navigation') || htmlIframe.getElementById('contentFrame')
        this.$nextTick(() => {
          const top = this.checkIframePositionSimple(htmlIframe)
          if (navIframe) {
            if (top) {
              navIframe.style.height = `calc(100vh - ${top}px)`; // 减去导航高度
            }
            // navIframe.srcdoc = handleCode(this.childUrl, !isApp);
            navIframe.src = this.childUrl
            const iframeKeydownHandler=(e) => {
              this.keyboardEvents(e)
            }
            navIframe.addEventListener('load', () => {
              const navIframeDoc = navIframe.contentDocument || navIframe.contentWindow.document;
              this.childIframe = useEventListener(navIframeDoc, 'keydown', iframeKeydownHandler)
            });
          }
          var homeMenu = htmlIframe.querySelector(`[data-uuid="${this.pageUuid}"]`)
          let currentMenu = htmlIframe.querySelector('.active-menu')
          if (homeMenu) {
              currentMenu?.classList.remove('active-menu')
              homeMenu.classList.add('active-menu');
          }
        })
      }
    },
    // 获取子页面位置信息
    checkIframePositionSimple(htmlIframe) {
      const iframe = htmlIframe.getElementById('navigation');
      if (iframe) {
        const iframeRect = iframe.getBoundingClientRect();
        return iframeRect.top
      }
      return
    },
    renderIframe(pageHtml) {
      // const isApp = this.pageType == 'app'
      // let template = handleCode(pageHtml, !isApp);
      // let iframe = document.getElementById('iframe')
      // if (isApp) {
      //   iframe = document.getElementById('iframeApp')
      // }
      // if(isIOSWechat()) {
      //     const parser = new DOMParser();
      //     const doc = parser.parseFromString(template, 'text/html');
      //     const updatedHtmlString = new XMLSerializer().serializeToString(doc);
      //     const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
      //     iframeDocument.write(updatedHtmlString);
      //     return
      // }
      // if(!this.isHtml) {
      //   return
      // }
      // iframe.srcdoc = template
    },
    // 点击目录切换页面
    handleChangePage(node) {
      if (!node.folderFlag) {
        this.pageName = node.pageName
        this.pageType = node.pageScene
        this.$nextTick(()=>{
          this.getAppPageVersion(node)
        })
        if (this.drag) {
          this.drag.hide()
        }
      }
      this.currentIndex = this.pageList.findIndex(item=>item.pageUuid == node.uuid) || 0;
      this.pageUuid = node.uuid
    },
    changeResolution() {
      if (this.pageType === 'app') {
        const contentApp = document.querySelector('.preview-suitable-content-app')
        // contentApp.style.aspectRatio = Number(this.previewSizeW)/Number(this.previewSizeH)
        const borderDom = document.querySelector('.app-border')
        const scale = Math.min(contentApp.offsetWidth/Number(this.previewSizeW), contentApp.offsetHeight/Number(this.previewSizeH))
        borderDom.style.transform = `scale(${scale})`
      } else {
        if (this.appName) {
          const contentApp = document.querySelector('.page-content')
          let borderDom = this.isHtml ? document.getElementById('iframe') :  document.getElementById('vueIframeWeb')
          const scale = Math.min(contentApp.offsetWidth/Number(this.previewSizeW), contentApp.offsetHeight/Number(this.previewSizeH))
          borderDom.style.transform = `scale(${scale})`
        }
      }
    },
    changeCurrentIndex(num) {
      if (num == -1) {
        if (this.currentIndex > 0) {
          this.currentIndex--
        }
      } else {
        if (this.currentIndex < this.pageList.length - 1) {
          this.currentIndex++
        }
      }
      this.handleChangePage(this.pageList[this.currentIndex])
    },
    // 键盘事件
    keyboardEvents(event) {
      if (event.key === 'ArrowLeft') {
        // 向左键：移动到前一个项目，如果已经是第一个则不处理
        event.preventDefault();
        this.changeCurrentIndex(-1)
      } else if (event.key === 'ArrowRight') {
        // 向右键：移动到下一个项目，如果已经是最后一个则不处理
        event.preventDefault();
        this.changeCurrentIndex(1)
      } else if (event.key === 'Escape') {
        this.isPreview = false
        this.isShowTip = false
        clearTimeout(this.setTimeout1)
        this.setTimeout1 = null
      }
    },
    createKeyboardNavigation() {
      // 处理键盘事件
      const handleKeyDown = (event) => {
        if (this.pageList.length === 0) return;
        this.keyboardEvents(event)
      };
      // 添加事件监听
      window.addEventListener('keydown', handleKeyDown);
    
      // 返回一个移除事件监听的函数
      return () => {
        window.removeEventListener('keydown', handleKeyDown);
      };
    },
    toPreview() {
      this.isPreview = true
      this.isShowTip = true
      this.setTimeout1 = setTimeout(()=>{
        this.isShowTip = false
      }, 5000)
    },
    vueIfameloaded() {
      this.$nextTick(() => {
        const iframeId = this.pageType === 'app' ? '#vueIframeApp' : '#vueIframeWeb'
        const iframeApp = document.querySelector(iframeId);
        // const iframeAppDoc = iframeApp.contentDocument || iframeApp.contentWindow.document;
        // const tag = iframeAppDoc.querySelector('.ai-tag')
        // tag && (tag.style && (tag.style.visibility = 'hidden') || tag.style.setAtrrbute('visibility','hidden'))
      })
    }
  },
  beforeDestroy() {
    this.cleanup()
    this.drag.destroy()
    this.drag = null
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
    }
    if (this.iframeMessage) {
        this.iframeMessage()
        this.iframeMessage = null
    }
    if (this.childIframe) {
      this.childIframe()
      this.childIframe = null
    }
  }
})
app.component('treeNode', treeNode);
app.mount('#app')

// 过滤用户没有生成的页面
function filterByHasVersion(data) {
  // 如果不是数组，直接返回
  if (!Array.isArray(data)) return data;

  // 使用 filter 移除 hasVersion === 1 的对象
  return data.filter(item => {
    if (item.hasVersion === '1') {
      return false; // 移除该对象
    }

    // 递归处理 children
    if (item.children && Array.isArray(item.children)) {
      item.children = filterByHasVersion(item.children);
    }

    return true; // 保留该对象
  });
}

/**
 * 用于遍历嵌套数组中 folderFlag 为 false 的对象
 * @param {Array} items - 要遍历的嵌套数组
 */
function collectItems(nodes, flatItems) {
  nodes.forEach((node) => {
    
    if (node.folderFlag === false) {
      flatItems.push({
        ...node,
      });
    }
    
    if (node.childrenList && node.childrenList.length > 0) {
      collectItems(node.childrenList, flatItems);
    }
  });
}