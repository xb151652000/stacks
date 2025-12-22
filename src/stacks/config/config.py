"""
Stacks配置管理模块
此模块提供配置文件的加载、验证、保存和实时更新功能。
使用YAML格式的配置文件，支持线程安全的配置操作。
"""

import threading
import logging
import yaml
import copy
from stacks.constants import CONFIG_FILE, CONFIG_SCHEMA_FILE
from stacks.config.validate import _validate, ensure_login_credentials

logger = logging.getLogger('config')

class Config:
    """
    配置加载器，支持实时更新
    提供线程安全的配置管理功能，包括：
    - 从YAML文件加载配置
    - 根据模式验证配置
    - 保存配置到文件
    - 获取和设置配置值
    - 确保登录凭据存在
    """

    def __init__(self, config_path=CONFIG_FILE, schema_path=CONFIG_SCHEMA_FILE):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
            schema_path: 配置模式文件路径
        """
        self.config_path = config_path      # 配置文件路径
        self.schema_path = schema_path      # 配置模式文件路径
        self.lock = threading.Lock()        # 线程锁，确保线程安全

        # 加载配置和模式
        self.load_schema()  # 加载配置模式（验证规则）
        self.load()         # 加载配置数据

        # 验证和修复配置
        olddata = copy.deepcopy(self.data)  # 保存原始数据用于比较
        self.data = self.validate(self.data, self.schema)  # 验证配置
        self.ensure_login_credentials()  # 确保登录凭据存在
        
        # 如果配置被修复，保存更新后的配置
        if not self.data == olddata:
            logger.info("配置文件中的某些值不符合标准。配置文件已被修复。")
            self.save()
        

    def load(self):
        """
        从文件加载配置，如果文件不存在则创建空字典
        使用YAML安全加载器解析配置文件，确保安全性。
        """
        with self.lock:  # 获取线程锁
            try:
                with open(self.config_path, "r") as f:
                    # 使用YAML安全加载器，防止执行任意代码
                    self.data = yaml.safe_load(f) or {}
                    logger.debug("配置已加载。")
            except FileNotFoundError:
                # 配置文件不存在，创建空配置供后续填充
                logger.debug("未找到配置文件，正在创建空配置以供填充。")
                self.data = {}

    def load_schema(self):
        """
        从文件加载配置模式
        配置模式定义了配置文件的结构、类型和验证规则。
        """
        with self.lock:  # 获取线程锁
            with open(self.schema_path, "r") as f:
                self.schema = yaml.safe_load(f)
                logger.debug("配置模式已加载。")

    def save(self):
        """
        将配置保存到文件
        使用YAML格式保存配置，保持可读性和结构化。
        """
        with self.lock:  # 获取线程锁
            with open(self.config_path, "w") as f:
                # 保存配置，禁用流式样式以保持可读性，不排序键以保持顺序
                yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
                logger.debug("配置文件已保存。")

    def validate(self, data, schema):
        """
        调用模式验证器来规范化配置
        根据配置模式验证和规范化配置数据，确保配置符合预定义的规则。
        
        Args:
            data: 要验证的配置数据
            schema: 配置模式
            
        Returns:
            dict: 验证和规范化后的配置数据
        """
        return _validate(data, schema)
    
    def get(self, *keys, default=None):
        """
        获取嵌套配置值
        支持通过多个键访问深层嵌套的配置值。
        
        Args:
            *keys: 配置键的序列，如("server", "port")
            default: 如果键不存在时返回的默认值
            
        Returns:
            配置值或默认值
        """
        with self.lock:  # 获取线程锁
            value = self.data
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return default
                if value is None:
                    return default
            return value
    
    def ensure_login_credentials(self):
        """
        确保登录凭据存在
        如果配置中没有登录凭据，则创建默认凭据。
        这是系统安全的基本要求。
        """
        return ensure_login_credentials(self)
    
    
    def set(self, *keys, value):
        """
        设置嵌套配置值
        支持设置深层嵌套的配置值，如果中间路径不存在则自动创建。
        
        Args:
            *keys: 配置键的序列，最后一个键是要设置的键
            value: 要设置的值
        """
        with self.lock:  # 获取线程锁
            # 导航到父级对象
            data = self.data
            for key in keys[:-1]:
                if key not in data:
                    data[key] = {}  # 创建中间路径
                data = data[key]
            # 设置值
            data[keys[-1]] = value
    
    def get_all(self):
        """
        获取整个配置作为字典
        返回配置数据的副本，防止外部修改影响内部状态。
        
        Returns:
            dict: 配置数据的副本
        """
        with self.lock:  # 获取线程锁
            return self.data.copy()