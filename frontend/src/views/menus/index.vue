<template>
  <div class="page-container">
    <!-- 操作按钮 -->
    <div class="table-actions mb-20">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增菜单
      </el-button>
    </div>
    
    <!-- 菜单表格 -->
    <el-table
      :data="menuList"
      v-loading="loading"
      row-key="id"
      border
      default-expand-all
    >
      <el-table-column prop="name" label="菜单名称" />
      <el-table-column prop="icon" label="图标" width="100">
        <template #default="{ row }">
          <el-icon v-if="row.icon"><component :is="row.icon" /></el-icon>
        </template>
      </el-table-column>
      <el-table-column prop="path" label="路由路径" />
      <el-table-column prop="component" label="组件路径" />
      <el-table-column prop="order_num" label="排序" width="80" />
      <el-table-column prop="is_visible" label="可见" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_visible ? 'success' : 'info'">
            {{ row.is_visible ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_enabled" label="启用" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_enabled ? 'success' : 'danger'">
            {{ row.is_enabled ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleAdd(row)">添加子菜单</el-button>
          <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="上级菜单">
          <el-tree-select
            v-model="formData.parent_id"
            :data="menuTreeData"
            :props="{ label: 'name', value: 'id' }"
            placeholder="选择上级菜单"
            clearable
            check-strictly
          />
        </el-form-item>
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="formData.name" />
        </el-form-item>
        <el-form-item label="菜单类型">
          <el-radio-group v-model="formData.menu_type">
            <el-radio value="menu">菜单</el-radio>
            <el-radio value="button">按钮</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="formData.icon" placeholder="Element Plus图标名称" />
        </el-form-item>
        <el-form-item label="路由路径">
          <el-input v-model="formData.path" />
        </el-form-item>
        <el-form-item label="组件路径">
          <el-input v-model="formData.component" />
        </el-form-item>
        <el-form-item label="权限标识">
          <el-input v-model="formData.permission" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="formData.order_num" :min="0" />
        </el-form-item>
        <el-form-item label="是否可见">
          <el-switch v-model="formData.is_visible" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="formData.is_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { getMenuTree, createMenu, updateMenu, deleteMenu } from '@/api/menu'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const menuList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const formData = reactive({
  id: null,
  parent_id: null,
  name: '',
  menu_type: 'menu',
  icon: '',
  path: '',
  component: '',
  permission: '',
  order_num: 0,
  is_visible: true,
  is_enabled: true
})

const formRules = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑菜单' : '新增菜单')

const menuTreeData = computed(() => {
  return [{ id: null, name: '顶级菜单', children: menuList.value }]
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getMenuTree()
    menuList.value = res
  } catch (error) {
    console.error('加载菜单列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 新增
const handleAdd = (parent = null) => {
  isEdit.value = false
  Object.assign(formData, {
    id: null,
    parent_id: parent?.id || null,
    name: '',
    menu_type: 'menu',
    icon: '',
    path: '',
    component: '',
    permission: '',
    order_num: 0,
    is_visible: true,
    is_enabled: true
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 提交
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  try {
    if (isEdit.value) {
      await updateMenu(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await createMenu(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该菜单吗？', '提示', {
      type: 'warning'
    })
    await deleteMenu(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 初始化
loadData()
</script>
