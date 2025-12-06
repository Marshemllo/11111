import request from './request'

/**
 * 获取菜单树
 */
export function getMenuTree() {
  return request.get('/menus/tree')
}

/**
 * 获取菜单列表
 */
export function getMenuList() {
  return request.get('/menus')
}

/**
 * 获取菜单详情
 */
export function getMenuDetail(id) {
  return request.get(`/menus/${id}`)
}

/**
 * 创建菜单
 */
export function createMenu(data) {
  return request.post('/menus', data)
}

/**
 * 更新菜单
 */
export function updateMenu(id, data) {
  return request.put(`/menus/${id}`, data)
}

/**
 * 删除菜单
 */
export function deleteMenu(id) {
  return request.delete(`/menus/${id}`)
}

/**
 * 调整菜单排序
 */
export function updateMenuOrder(id, orderNum) {
  return request.put(`/menus/${id}/order`, null, { params: { order_num: orderNum } })
}
