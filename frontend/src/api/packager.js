import axios from "axios";

// 设置 API 基础 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://zgcc.online/zgcc/api/packager";

/* 用户登录 */
export const userLogin = async (username, password) => {
    const response = await axios.post(`${API_BASE_URL}/login/`, { username, password });
    return response.data;
};

/* 保存货物信息 */
export const saveFreight = async (username, freightData) => {
    const response = await axios.post(`${API_BASE_URL}/freight/`, {
      username,         // 传给后端用来查找 User
      freight_data: freightData, // 货物信息数组
    });
    return response.data; // 例如 { success: true, message: '货物信息已保存！' }
};

/* 生成装箱方案 */
export const generatePackingPlan = async (goodsList, stdInfo, outerLimit) => {
  const response = await axios.post(`${API_BASE_URL}/plan/`, {
    goodsList,
    stdInfo,
    outerLimit
  });
  return response.data; // { success: true, plan: [...] }
};