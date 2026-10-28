---
来源站点: javaup.chat（码力全开）
原文链接: https://javaup.chat/tools/docker/practical-guide/
抓取日期: 2026-10-28
所属知识域: 域4 工程交付与云原生
板块: Docker-安装与实战
---

# Docker 安装配置与实战操作

## 环境与加速

- Windows/macOS：Docker Desktop；Linux：`get.docker.com` + `systemctl enable docker`；非 root：`usermod -aG docker $USER`
- 国内镜像加速：`/etc/docker/daemon.json` → `registry-mirrors`

## 镜像与容器高频命令

```bash
docker pull redis:7.0
docker images / docker rmi / docker image prune
docker save -o redis.tar redis:7.0 && docker load -i redis.tar
docker run -d -p 8080:80 --name web --restart=unless-stopped nginx:1.23
docker logs -f --tail 100 web
docker exec -it web bash
docker cp ./config.json web:/app/config.json
```

## 资源限制与网络

```bash
docker run -d --cpus="1.5" --memory="1g" --memory-swap="1g" myapp:latest
docker network create app-network
# 同网络内容器可用服务名互访
```

## 数据持久化

- **Volume（推荐生产）**：`docker volume create app-data` + `-v app-data:/var/lib/postgresql/data`
- **Bind Mount（开发）**：`-v $(pwd)/src:/app/src` 或 `:ro`
- 备份：临时容器 `tar czf` 挂载卷目录

## 完整 Web 栈骨架

network → postgres(+volume) → api(+env DATABASE_URL) → nginx(-p 80:80)
