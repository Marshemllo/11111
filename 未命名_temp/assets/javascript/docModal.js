const DraggableResizableModal = class DraggableResizableModal {
    constructor() {
        this.modal = document.getElementById('modal');
        this.mask = document.getElementById('vditor-mask');
        this.modalContent = document.getElementById('modalContent');
        this.closeBtn = document.getElementById('closeModal');
        
        // 拖拽状态变量
        this.isDragging = false;
        this.isResizing = false;
        this.resizeDirection = '';
        
        // 初始位置和尺寸
        this.startX = 0;
        this.startY = 0;
        this.startLeft = 0;
        this.startTop = 0;
        this.minModalWidth = 320;
        this.minModalHeight = 320;
        
        this.vditor = null
        this.init();
    }

    init() {
        // 绑定事件
        this.bindEvents();
        this.initModal();
        this.vditor = new Vditor('vditor', {
            cdn: './assets/vditor',
            // 必须单独配置主题路径
            preview: {
                theme: {
                path: './assets/vditor/dist/css/content-theme'
                }
            },
            
            // 表情图标路径
            emojiPath: './assets/vditor/dist/images/emoji',
            toolbar: [],
            mode: 'wysiwyg'
        });
    }

    bindEvents() {
        // 关闭模态框
        this.closeBtn.addEventListener('click', () => {
            this.hide();
        });
        
        // 绑定拖拽事件
        this.modal.addEventListener('mousedown', (e) => {
            this.startDrag(e);
        });
        
        // 绑定调整大小事件
        const resizeHandles = document.querySelectorAll('.resize-handle');
        resizeHandles.forEach(handle => {
            handle.addEventListener('mousedown', (e) => {
                this.startResize(e);
            });
        });
        
        // 全局鼠标事件
        document.addEventListener('mousemove', (e) => {
            this.handleMouseMove(e);
        });
        // 全局鼠标释放事件
        document.addEventListener('mouseup', () => {
            this.handleMouseUp();
        });
    }
  
    // 显示模态框
    async show(appuuid, pageUuid) {
        if (this.modal.classList.contains('show')) {
            return
        }
        const messageText = appDoc[pageUuid] || ''
        this.vditor.setValue(messageText || '')
        this.modal.classList.add('show')
        this.modal.querySelector('.modal-content').scrollTop = 0
        if (messageText) {
            this.modalContent.querySelector('#vditor').classList.remove('hide')
            this.modalContent.querySelector('.doc-empty-data').classList.remove('show')
        } else {
            this.modalContent.querySelector('#vditor').classList.add('hide')
            this.modalContent.querySelector('.doc-empty-data').classList.add('show')
        }
        this.initModal()
    }
    
    // 隐藏模态框
    hide() {
        this.modal.classList.remove('show')
    }
    
    // 初始化模态框
    initModal() {
        const offset = 29
        this.modal.style.left = `${(window.innerWidth - this.minModalWidth - offset) * 100 / window.innerWidth}%`;
        this.modal.style.right = `${29 * 100 / window.innerWidth}%`;
        this.modal.style.top = `${70 * 100 / window.innerHeight}%`;
        this.modal.style.bottom = `${70 * 100 / window.innerHeight}%`;
    }
  
    // 开始拖拽
    startDrag(e) {
        if (!this.mask.classList.contains('show')) {
            this.mask.classList.add('show')
        }
        this.isResizing = false;
        this.isDragging = true;
        this.startX = e.clientX;
        this.startY = e.clientY;
        this.startLeft = this.modal.offsetLeft;
        this.startTop = this.modal.offsetTop;
        
        e.preventDefault();
    }
  
    // 开始调整大小
    startResize(e) {
        if (!this.mask.classList.contains('show')) {
            this.mask.classList.add('show')
        }
        this.isDragging = false;
        this.isResizing = true;
        this.resizeDirection = e.target.getAttribute('data-direction');
        this.startX = e.clientX;
        this.startY = e.clientY;
        this.startLeft = this.modal.offsetLeft;
        this.startTop = this.modal.offsetTop;
        
        e.preventDefault();
        e.stopPropagation();
    }
  
    // 处理鼠标移动
    handleMouseMove(e) {
        if (this.isDragging) {
            this.handleDrag(e);
        } else if (this.isResizing) {
            this.handleResize(e);
        }
    }
  
    // 处理拖拽
    handleDrag(e) {
        const deltaX = e.clientX - this.startX;
        const deltaY = e.clientY - this.startY;
        
        let newLeft = this.startLeft + deltaX;
        let newTop = this.startTop + deltaY;
        
        // 边界限制
        newLeft = Math.max(0, Math.min(newLeft, window.innerWidth - this.modal.offsetWidth));
        newTop = Math.max(0, Math.min(newTop, window.innerHeight - this.modal.offsetHeight));

        const trueLeft = parseFloat(this.modal.style.left) * window.innerWidth / 100
        const trueTop = parseFloat(this.modal.style.top) * window.innerHeight / 100
        const trueRight= parseFloat(this.modal.style.right) * window.innerWidth / 100
        const trueTBottom = parseFloat(this.modal.style.bottom) * window.innerHeight / 100
        
        const newDeltaX = newLeft - trueLeft
        const newDeltaY = newTop - trueTop

        this.modal.style.left = newLeft * 100 / window.innerWidth + '%';
        this.modal.style.top = newTop * 100 / window.innerHeight + '%';
        this.modal.style.right = (trueRight - newDeltaX) * 100 / window.innerWidth + '%';
        this.modal.style.bottom = (trueTBottom - newDeltaY) * 100 / window.innerHeight + '%';
    }
    // 处理调整大小
    handleResize(e) {
        const offset = 1
        const trueTop = parseFloat(this.modal.style.top) * window.innerHeight / 100
        const trueRight= parseFloat(this.modal.style.right) * window.innerWidth / 100
        const trueTBottom = parseFloat(this.modal.style.bottom) * window.innerHeight / 100
        const trueLeft = parseFloat(this.modal.style.left) * window.innerWidth / 100
        switch (this.resizeDirection) {
            case 'top':
                const maxTop = window.innerHeight - trueTBottom - this.minModalHeight
                this.modal.style.top = Math.max(0, Math.min(e.clientY, maxTop)) * 100 / window.innerHeight + '%';
                break;
            case 'right':
                const maxRight = window.innerWidth - (trueLeft + this.minModalWidth)
                this.modal.style.right = Math.max(0, Math.min(window.innerWidth - e.clientX - offset, maxRight)) * 100 / window.innerWidth + '%';
                break;
            case 'bottom':
                const maxBottom = window.innerHeight - (trueTop + this.minModalHeight)
                this.modal.style.bottom = Math.max(0, Math.min(window.innerHeight - e.clientY - offset, maxBottom)) * 100 / window.innerHeight + '%';
                break;
            case 'left':
                const maxLeft = window.innerWidth - trueRight - this.minModalWidth
                this.modal.style.left = Math.max(0, Math.min(e.clientX, maxLeft)) * 100 / window.innerWidth + '%';
                break;
        }
    }
  
    // 处理鼠标释放
    handleMouseUp() {
        this.isDragging = false;
        this.isResizing = false;
        this.resizeDirection = '';
        this.mask.classList.remove('show')
    }
    destroy() {
        this.vditor.destroy()
        this.destroyed = null
    }
}