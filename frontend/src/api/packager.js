import axios from "axios";

// 设置 API 基础 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://zgcc.online/zgcc/api/packager";

export const userLogin = async (username, password) => {
    const response = await axios.post(`${API_BASE_URL}/login/`, { username, password });
    return response.data;
};
