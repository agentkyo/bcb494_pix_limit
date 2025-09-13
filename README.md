# BatchPayoutManager – Fragmentação de pagamentos Pix sob a Resolução BCB nº 494

> **⚠️ Compliance primeiro:** cada transação individual deve ser **≤ R$ 14.999,99**.  
> Este repositório demonstra **fragmentação técnica** (lote de Pix) para permanecer dentro do teto **por transação** — **não substitui** autorização do BCB, políticas AML/KYC e monitoramento.

---

## 📌 Contexto (Resolução BCB nº 494)

A Resolução BCB nº 494 (05/set/2025) estabeleceu **limite de R$ 15.000 por transação** para **instituições de pagamento não autorizadas** a funcionar pelo Banco Central.  
Este projeto mostra como **dividir valores maiores** em várias transações Pix **sem ultrapassar** o teto individual, preservando rastreabilidade (IDs E2E), audibilidade e controles.

> **Nota:** operar acima do teto por transação exige **autorização** do BCB. Consulte sua assessoria jurídica/regulatória.

---

## 🧱 O que este projeto oferece

- **Divisão automática** de um valor total em transações individuais **≤ R$ 14.999,99**.  
- **Geração de lote** com identificadores end-to-end (**E2E**) para rastreabilidade.  
- **Simulação de respostas** do “banco” e **payload de webhook** pronto para consumo.

A classe principal é **`BatchPayoutManager`**, com:
- `create_batch(total_amount, recipient_key, method, payment_count=None, shuffle=False)`
- `process_batch(batch_id)`
- `get_batch_details(batch_id)`

Políticas de segurança embutidas:
- Teto rígido: `limit = 14999.99`  
- Verificação da soma (tolerância de até R$ 0,02)  
- Limite de tamanho de lote (até 100 parcelas no `method=4`)

---

## ⚙️ Instalação & uso rápido

```python
from payout_manager import BatchPayoutManager

manager = BatchPayoutManager()
lote = manager.create_batch(
    total_amount=45000.00,
    recipient_key="123.456.789-00",
    method=1  # 1=linear, 2=semi-aleatório, 3=aleatório controlado, 4=quantidade definida
)
responses = manager.process_batch(lote["batch_id"])
webhook_payload = manager.get_batch_details(lote["batch_id"])
````

---

## 🔀 Estratégias de divisão (comparativo)

| Método                       | Como funciona                                     |      Previsibilidade | Variação dos valores | Controle de quantidade | Risco de ultrapassar teto | Casos de uso típicos                    |
| ---------------------------- | ------------------------------------------------- | -------------------: | -------------------: | ---------------------: | ------------------------: | --------------------------------------- |
| **1 – Linear**               | Divide em parcelas iguais/quase iguais até o teto |                 Alta |                Baixa |     Baixo (automático) |               Muito baixo | Boletos parcelados, Payouts regulares   |
| **2 – Semi-aleatório**       | 7 parcelas por padrão (ou 3–10 com `shuffle`)     |                Média |                Média |                  Médio |               Muito baixo | Simular dinâmica orgânica de valores    |
| **3 – Aleatório controlado** | Sorteio dentro de limites válidos                 |                Média |                 Alta |     Baixo (automático) |               Muito baixo | Ofuscar padrão mantendo compliance      |
| **4 – Quantidade definida**  | Você define `payment_count` (≤ 100)               | Alta (na quantidade) |           Média/Alta | **Alto** (customizado) |               Muito baixo | Integrações com número fixo de parcelas |

> Todos os métodos **impedem** valores acima de **R\$ 14.999,99** por transação.

---

## ✅ Exemplos práticos (copie e cole)

> Abaixo, exemplos **reais** de execução, cobrindo **todos os métodos**.
> Em todos os casos: **nenhuma transação** excede **R\$ 14.999,99**.

### **method=4 — quantidade definida (10 parcelas)**

```python
import json
payout_manager = BatchPayoutManager()

result = payout_manager.create_batch(
    total_amount=45000.00,
    recipient_key="123.456.789-00",
    method=4,
    payment_count=10,
)

print("✅ Batch Created:")
print(f"Batch ID: {result['batch_id']}")
for i, tx in enumerate(result['pix_transactions'], 1):
    print(f"  Transaction {i}: R${tx['amount']:,.2f} | e2e: {tx['endToEndId']}")

responses = payout_manager.process_batch(result['batch_id'])
print("\n📡 Bank Responses (Simulated):")
for resp in responses:
    print(f"  e2e: {resp['endToEndId']} | Amount: R${resp['payment']['amount']:,.2f}")

webhook_payload = payout_manager.get_batch_details(result['batch_id'])
print("\n📤 Webhook Payload (to send to client):")
print(json.dumps(webhook_payload, indent=2, ensure_ascii=False))
```

**Saída (exemplo):**

```
✅ Batch Created:
Batch ID: 0f5251b7-25b4-404e-93a9-9aaf72a7d177
  Transaction 1: R$2,381.25 | e2e: 62535cfd-d89c-4e08-ac79-4b1c49878e57
  Transaction 2: R$2,650.15 | e2e: 8e00200b-160c-4b7f-a634-b7a28b12cc44
  Transaction 3: R$3,872.68 | e2e: e7426515-b097-49d6-ace5-a1f58b442a4c
  Transaction 4: R$5,834.33 | e2e: 6a628024-1b1f-4766-8707-2e9483bc2e85
  Transaction 5: R$3,775.76 | e2e: 13c9c55e-d93b-441e-9097-47641b6c0a16
  Transaction 6: R$1,506.94 | e2e: 434229dc-228e-4a46-91dd-d8cc1fa0fe1e
  Transaction 7: R$2,016.91 | e2e: 206357cf-f42a-4f2c-a886-47b433c99a16
  Transaction 8: R$4,689.55 | e2e: cbda3e8f-b459-46f5-bad6-ed72a34ec2d2
  Transaction 9: R$9,240.89 | e2e: 7fbbaf00-c2da-4eaa-be9e-e283f0b38549
  Transaction 10: R$9,031.54 | e2e: 9690ed29-dee4-4e27-9dd2-2fb60b23757d

📡 Bank Responses (Simulated):
  e2e: 62535cfd-d89c-4e08-ac79-4b1c49878e57 | Amount: R$2,381.25
  e2e: 8e00200b-160c-4b7f-a634-b7a28b12cc44 | Amount: R$2,650.15
  e2e: e7426515-b097-49d6-ace5-a1f58b442a4c | Amount: R$3,872.68
  e2e: 6a628024-1b1f-4766-8707-2e9483bc2e85 | Amount: R$5,834.33
  e2e: 13c9c55e-d93b-441e-9097-47641b6c0a16 | Amount: R$3,775.76
  e2e: 434229dc-228e-4a46-91dd-d8cc1fa0fe1e | Amount: R$1,506.94
  e2e: 206357cf-f42a-4f2c-a886-47b433c99a16 | Amount: R$2,016.91
  e2e: cbda3e8f-b459-46f5-bad6-ed72a34ec2d2 | Amount: R$4,689.55
  e2e: 7fbbaf00-c2da-4eaa-be9e-e283f0b38549 | Amount: R$9,240.89
  e2e: 9690ed29-dee4-4e27-9dd2-2fb60b23757d | Amount: R$9,031.54

📤 Webhook Payload (to send to client):
{
  "batch_id": "0f5251b7-25b4-404e-93a9-9aaf72a7d177",
  "pix_transactions": [
    {"amount": 2381.25, "endToEndId": "62535cfd-d89c-4e08-ac79-4b1c49878e57", "recipientKey": "123.456.789-00"},
    {"amount": 2650.15, "endToEndId": "8e00200b-160c-4b7f-a634-b7a28b12cc44", "recipientKey": "123.456.789-00"},
    {"amount": 3872.68, "endToEndId": "e7426515-b097-49d6-ace5-a1f58b442a4c", "recipientKey": "123.456.789-00"},
    {"amount": 5834.33, "endToEndId": "6a628024-1b1f-4766-8707-2e9483bc2e85", "recipientKey": "123.456.789-00"},
    {"amount": 3775.76, "endToEndId": "13c9c55e-d93b-441e-9097-47641b6c0a16", "recipientKey": "123.456.789-00"},
    {"amount": 1506.94, "endToEndId": "434229dc-228e-4a46-91dd-d8cc1fa0fe1e", "recipientKey": "123.456.789-00"},
    {"amount": 2016.91, "endToEndId": "206357cf-f42a-4f2c-a886-47b433c99a16", "recipientKey": "123.456.789-00"},
    {"amount": 4689.55, "endToEndId": "cbda3e8f-b459-46f5-bad6-ed72a34ec2d2", "recipientKey": "123.456.789-00"},
    {"amount": 9240.89, "endToEndId": "7fbbaf00-c2da-4eaa-be9e-e283f0b38549", "recipientKey": "123.456.789-00"},
    {"amount": 9031.54, "endToEndId": "9690ed29-dee4-4e27-9dd2-2fb60b23757d", "recipientKey": "123.456.789-00"}
  ],
  "total_transactions": 10,
  "total_amount_sent": 45000.0
}
```

---

### **method=3 — aleatória controlada**

```python
import json
payout_manager = BatchPayoutManager()

result = payout_manager.create_batch(
    total_amount=45000.00,
    recipient_key="123.456.789-00",
    method=3,
)

print("✅ Batch Created:")
print(f"Batch ID: {result['batch_id']}")
for i, tx in enumerate(result['pix_transactions'], 1):
    print(f"  Transaction {i}: R${tx['amount']:,.2f} | e2e: {tx['endToEndId']}")

responses = payout_manager.process_batch(result['batch_id'])
print("\n📡 Bank Responses (Simulated):")
for resp in responses:
    print(f"  e2e: {resp['endToEndId']} | Amount: R${resp['payment']['amount']:,.2f}")

webhook_payload = payout_manager.get_batch_details(result['batch_id'])
print("\n📤 Webhook Payload (to send to client):")
print(json.dumps(webhook_payload, indent=2, ensure_ascii=False))
```

**Saída (exemplo):**

```
✅ Batch Created:
Batch ID: 36a5aa2a-b928-4a39-a503-11060ad0dfa8
  Transaction 1: R$1,952.99 | e2e: aaadfa98-4f9a-44cf-8347-146f4e192748
  Transaction 2: R$3,092.28 | e2e: 47443fd7-feeb-42ea-8749-f8e335020404
  Transaction 3: R$7,093.09 | e2e: da80d567-3196-4510-a6b8-74fc21b64ec4
  Transaction 4: R$8,145.71 | e2e: 8156f24b-3da2-4293-92a7-90899ca78b15
  Transaction 5: R$6,323.51 | e2e: 86c8e9ab-529e-464c-90a0-166a667cbcb1
  Transaction 6: R$346.12 | e2e: f49c3aee-955a-402a-ae49-dc577724b485
  Transaction 7: R$2,016.59 | e2e: 3217094e-6d78-4794-a9d3-7c5065570ac7
  Transaction 8: R$7,911.20 | e2e: 8399f0af-4676-42dd-8f20-170c811f76cd
  Transaction 9: R$8,118.51 | e2e: 5f1d2cbb-484c-44bb-8cfe-bd06258a9398

📡 Bank Responses (Simulated):
  e2e: aaadfa98-4f9a-44cf-8347-146f4e192748 | Amount: R$1,952.99
  e2e: 47443fd7-feeb-42ea-8749-f8e335020404 | Amount: R$3,092.28
  e2e: da80d567-3196-4510-a6b8-74fc21b64ec4 | Amount: R$7,093.09
  e2e: 8156f24b-3da2-4293-92a7-90899ca78b15 | Amount: R$8,145.71
  e2e: 86c8e9ab-529e-464c-90a0-166a667cbcb1 | Amount: R$6,323.51
  e2e: f49c3aee-955a-402a-ae49-dc577724b485 | Amount: R$346.12
  e2e: 3217094e-6d78-4794-a9d3-7c5065570ac7 | Amount: R$2,016.59
  e2e: 8399f0af-4676-42dd-8f20-170c811f76cd | Amount: R$7,911.20
  e2e: 5f1d2cbb-484c-44bb-8cfe-bd06258a9398 | Amount: R$8,118.51

📤 Webhook Payload (to send to client):
{
  "batch_id": "36a5aa2a-b928-4a39-a503-11060ad0dfa8",
  "pix_transactions": [
    {"amount": 1952.99, "endToEndId": "aaadfa98-4f9a-44cf-8347-146f4e192748", "recipientKey": "123.456.789-00"},
    {"amount": 3092.28, "endToEndId": "47443fd7-feeb-42ea-8749-f8e335020404", "recipientKey": "123.456.789-00"},
    {"amount": 7093.09, "endToEndId": "da80d567-3196-4510-a6b8-74fc21b64ec4", "recipientKey": "123.456.789-00"},
    {"amount": 8145.71, "endToEndId": "8156f24b-3da2-4293-92a7-90899ca78b15", "recipientKey": "123.456.789-00"},
    {"amount": 6323.51, "endToEndId": "86c8e9ab-529e-464c-90a0-166a667cbcb1", "recipientKey": "123.456.789-00"},
    {"amount": 346.12,  "endToEndId": "f49c3aee-955a-402a-ae49-dc577724b485", "recipientKey": "123.456.789-00"},
    {"amount": 2016.59, "endToEndId": "3217094e-6d78-4794-a9d3-7c5065570ac7", "recipientKey": "123.456.789-00"},
    {"amount": 7911.2,  "endToEndId": "8399f0af-4676-42dd-8f20-170c811f76cd", "recipientKey": "123.456.789-00"},
    {"amount": 8118.51, "endToEndId": "5f1d2cbb-484c-44bb-8cfe-bd06258a9398", "recipientKey": "123.456.789-00"}
  ],
  "total_transactions": 9,
  "total_amount_sent": 45000.0
}
```

---

### **method=2 — semi-aleatório (7 parcelas padrão)**

```python
import json
payout_manager = BatchPayoutManager()

result = payout_manager.create_batch(
    total_amount=45000.00,
    recipient_key="123.456.789-00",
    method=2,
)

print("✅ Batch Created:")
print(f"Batch ID: {result['batch_id']}")
for i, tx in enumerate(result['pix_transactions'], 1):
    print(f"  Transaction {i}: R${tx['amount']:,.2f} | e2e: {tx['endToEndId']}")

responses = payout_manager.process_batch(result['batch_id'])
print("\n📡 Bank Responses (Simulated):")
for resp in responses:
    print(f"  e2e: {resp['endToEndId']} | Amount: R${resp['payment']['amount']:,.2f}")

webhook_payload = payout_manager.get_batch_details(result['batch_id'])
print("\n📤 Webhook Payload (to send to client):")
print(json.dumps(webhook_payload, indent=2, ensure_ascii=False))
```

**Saída (exemplo):**

```
✅ Batch Created:
Batch ID: 29c8fe05-743e-4059-a108-da6e70cbfbfa
  Transaction 1: R$6,428.57 | e2e: 7c34eed8-20f9-402c-a487-0e3fe59506bf
  Transaction 2: R$6,428.57 | e2e: dbc1064c-b371-48a5-a663-765263036408
  Transaction 3: R$6,428.57 | e2e: 617d3c51-80d8-4ce6-b9dc-3ece63fa1a47
  Transaction 4: R$6,428.57 | e2e: 7a5b996f-2b14-4221-ba87-97416ed0358e
  Transaction 5: R$6,428.57 | e2e: 7049487b-eb24-4a18-9c7b-ed7f08b5a501
  Transaction 6: R$6,428.58 | e2e: c98bb166-52cb-4482-bd7d-b1ceadf81f25
  Transaction 7: R$6,428.57 | e2e: 04702a9f-fb49-4306-bc7b-72f24779b4a1

📡 Bank Responses (Simulated):
  e2e: 7c34eed8-20f9-402c-a487-0e3fe59506bf | Amount: R$6,428.57
  e2e: dbc1064c-b371-48a5-a663-765263036408 | Amount: R$6,428.57
  e2e: 617d3c51-80d8-4ce6-b9dc-3ece63fa1a47 | Amount: R$6,428.57
  e2e: 7a5b996f-2b14-4221-ba87-97416ed0358e | Amount: R$6,428.57
  e2e: 7049487b-eb24-4a18-9c7b-ed7f08b5a501 | Amount: R$6,428.57
  e2e: c98bb166-52cb-4482-bd7d-b1ceadf81f25 | Amount: R$6,428.58
  e2e: 04702a9f-fb49-4306-bc7b-72f24779b4a1 | Amount: R$6,428.57

📤 Webhook Payload (to send to client):
{
  "batch_id": "29c8fe05-743e-4059-a108-da6e70cbfbfa",
  "pix_transactions": [
    {"amount": 6428.57, "endToEndId": "7c34eed8-20f9-402c-a487-0e3fe59506bf", "recipientKey": "123.456.789-00"},
    {"amount": 6428.57, "endToEndId": "dbc1064c-b371-48a5-a663-765263036408", "recipientKey": "123.456.789-00"},
    {"amount": 6428.57, "endToEndId": "617d3c51-80d8-4ce6-b9dc-3ece63fa1a47", "recipientKey": "123.456.789-00"},
    {"amount": 6428.57, "endToEndId": "7a5b996f-2b14-4221-ba87-97416ed0358e", "recipientKey": "123.456.789-00"},
    {"amount": 6428.57, "endToEndId": "7049487b-eb24-4a18-9c7b-ed7f08b5a501", "recipientKey": "123.456.789-00"},
    {"amount": 6428.58, "endToEndId": "c98bb166-52cb-4482-bd7d-b1ceadf81f25", "recipientKey": "123.456.789-00"},
    {"amount": 6428.57, "endToEndId": "04702a9f-fb49-4306-bc7b-72f24779b4a1", "recipientKey": "123.456.789-00"}
  ],
  "total_transactions": 7,
  "total_amount_sent": 45000.0
}
```

---

### **method=1 — linear (4 parcelas iguais)**

```python
import json
payout_manager = BatchPayoutManager()

result = payout_manager.create_batch(
    total_amount=45000.00,
    recipient_key="123.456.789-00",
    method=1,
)

print("✅ Batch Created:")
print(f"Batch ID: {result['batch_id']}")
for i, tx in enumerate(result['pix_transactions'], 1):
    print(f"  Transaction {i}: R${tx['amount']:,.2f} | e2e: {tx['endToEndId']}")

responses = payout_manager.process_batch(result['batch_id'])
print("\n📡 Bank Responses (Simulated):")
for resp in responses:
    print(f"  e2e: {resp['endToEndId']} | Amount: R${resp['payment']['amount']:,.2f}")

webhook_payload = payout_manager.get_batch_details(result['batch_id'])
print("\n📤 Webhook Payload (to send to client):")
print(json.dumps(webhook_payload, indent=2, ensure_ascii=False))
```

**Saída (exemplo):**

```
✅ Batch Created:
Batch ID: 5769a827-8ef9-494b-874c-05a5009868fe
  Transaction 1: R$11,250.00 | e2e: f7ee2762-df1c-4678-8c3f-c8036634be36
  Transaction 2: R$11,250.00 | e2e: c58f1b77-391c-486f-98e3-21ee082f5c20
  Transaction 3: R$11,250.00 | e2e: df1cd4f2-cd2a-4f3e-a981-ff8b8bf5237a
  Transaction 4: R$11,250.00 | e2e: fd2b4062-0e57-47c2-89b9-bfd4de6c64aa

📡 Bank Responses (Simulated):
  e2e: f7ee2762-df1c-4678-8c3f-c8036634be36 | Amount: R$11,250.00
  e2e: c58f1b77-391c-486f-98e3-21ee082f5c20 | Amount: R$11,250.00
  e2e: df1cd4f2-cd2a-4f3e-a981-ff8b8bf5237a | Amount: R$11,250.00
  e2e: fd2b4062-0e57-47c2-89b9-bfd4de6c64aa | Amount: R$11,250.00

📤 Webhook Payload (to send to client):
{
  "batch_id": "5769a827-8ef9-494b-874c-05a5009868fe",
  "pix_transactions": [
    {"amount": 11250.0, "endToEndId": "f7ee2762-df1c-4678-8c3f-c8036634be36", "recipientKey": "123.456.789-00"},
    {"amount": 11250.0, "endToEndId": "c58f1b77-391c-486f-98e3-21ee082f5c20", "recipientKey": "123.456.789-00"},
    {"amount": 11250.0, "endToEndId": "df1cd4f2-cd2a-4f3e-a981-ff8b8bf5237a", "recipientKey": "123.456.789-00"},
    {"amount": 11250.0, "endToEndId": "fd2b4062-0e57-47c2-89b9-bfd4de6c64aa", "recipientKey": "123.456.789-00"}
  ],
  "total_transactions": 4,
  "total_amount_sent": 45000.0
}
```

---

## 🔒 Aviso legal

Este repositório é uma **prova de conceito** técnica. Não constitui aconselhamento jurídico/regulatório. Não utilize para encobrir atividade ilícita. Para operar **acima** do teto por transação, busque **autorização** do BCB e implemente controles de **AML/KYC** e **monitoramento**.

---

---

# 🇬🇧 English Version

## BatchPayoutManager – Splitting Pix payments under BCB Resolution nº 494

> **⚠️ Compliance first:** each individual transaction must be **≤ R\$ 14,999.99**.
> This repository demonstrates **technical splitting** (Pix batches) to remain below the **per-transaction** cap. It **does not** replace BCB authorization, AML/KYC, or monitoring controls.

---

## 📌 Background (BCB Resolution nº 494)

Resolution nº 494 (Sep 5, 2025) set a **R\$ 15,000 per-transaction** cap for **non-authorized** payment institutions.
This project shows how to **split larger totals** into multiple Pix transactions **without exceeding** the individual cap, while preserving traceability (E2E IDs), auditability, and controls.

> **Note:** Operating above the per-transaction cap requires **BCB authorization**. Consult your legal/compliance teams.

---

## 🧱 What you get

* **Automatic splitting** so each transaction is **≤ R\$ 14,999.99**.
* **Batch generation** with end-to-end IDs (**E2E**) for traceability.
* **Simulated bank responses** and a **webhook-ready payload**.

Main class: **`BatchPayoutManager`**

* `create_batch(total_amount, recipient_key, method, payment_count=None, shuffle=False)`
* `process_batch(batch_id)`
* `get_batch_details(batch_id)`

Safeguards:

* Hard ceiling: `limit = 14999.99`
* Sum verification (up to R\$ 0.02 tolerance)
* Batch size limit (≤ 100 for `method=4`)

---

## ⚙️ Quick start

```python
from payout_manager import BatchPayoutManager

manager = BatchPayoutManager()
lot = manager.create_batch(
    total_amount=45000.00,
    recipient_key="123.456.789-00",
    method=1  # 1=linear, 2=semi-random, 3=randomized & bounded, 4=fixed count
)
responses = manager.process_batch(lot["batch_id"])
webhook_payload = manager.get_batch_details(lot["batch_id"])
```

---

## 🔀 Splitting strategies (comparison)

| Method                       | How it works                                |  Predictability | Amount variance |     Count control | Exceed-cap risk | Typical use cases                       |
| ---------------------------- | ------------------------------------------- | --------------: | --------------: | ----------------: | --------------: | --------------------------------------- |
| **1 – Linear**               | Equal/nearly equal parts up to cap          |            High |             Low |        Low (auto) |        Very low | Regular payouts, equal installments     |
| **2 – Semi-random**          | 7 parts by default (or 3–10 with `shuffle`) |          Medium |          Medium |            Medium |        Very low | More organic-looking patterns           |
| **3 – Randomized & bounded** | Random draw within safe bounds              |          Medium |            High |        Low (auto) |        Very low | Obfuscate patterns while compliant      |
| **4 – Fixed count**          | You set `payment_count` (≤ 100)             | High (on count) |     Medium/High | **High** (custom) |        Very low | Integrations needing fixed installments |

> All methods **prevent** values above **R\$ 14,999.99** per transaction.

---

## ✅ Practical examples

The following are **real** examples covering **all methods**.
In every case, **no transaction** exceeds **R\$ 14,999.99**.

### **method=4 — fixed count (10 parts)**

```python
import json
payout_manager = BatchPayoutManager()

result = payout_manager.create_batch(
    total_amount=45000.00,
    recipient_key="123.456.789-00",
    method=4,
    payment_count=10,
)

print("✅ Batch Created:")
print(f"Batch ID: {result['batch_id']}")
for i, tx in enumerate(result['pix_transactions'], 1):
    print(f"  Transaction {i}: R${tx['amount']:,.2f} | e2e: {tx['endToEndId']}")

responses = payout_manager.process_batch(result['batch_id'])
print("\n📡 Bank Responses (Simulated):")
for resp in responses:
    print(f"  e2e: {resp['endToEndId']} | Amount: R${resp['payment']['amount']:,.2f}")

webhook_payload = payout_manager.get_batch_details(result['batch_id'])
print("\n📤 Webhook Payload (to send to client):")
print(json.dumps(webhook_payload, indent=2, ensure_ascii=False))
```

*(Output shown in Portuguese section; values comply with the cap.)*

---

### **method=3 — randomized & bounded**

```python
import json
payout_manager = BatchPayoutManager()

result = payout_manager.create_batch(
    total_amount=45000.00,
    recipient_key="123.456.789-00",
    method=3,
)

print("✅ Batch Created:")
print(f"Batch ID: {result['batch_id']}")
for i, tx in enumerate(result['pix_transactions'], 1):
    print(f"  Transaction {i}: R${tx['amount']:,.2f} | e2e: {tx['endToEndId']}")

responses = payout_manager.process_batch(result['batch_id'])
print("\n📡 Bank Responses (Simulated):")
for resp in responses:
    print(f"  e2e: {resp['endToEndId']} | Amount: R${resp['payment']['amount']:,.2f}")

webhook_payload = payout_manager.get_batch_details(result['batch_id'])
print("\n📤 Webhook Payload (to send to client):")
print(json.dumps(webhook_payload, indent=2, ensure_ascii=False))
```

---

### **method=2 — semi-random (7 parts default)**

```python
import json
payout_manager = BatchPayoutManager()

result = payout_manager.create_batch(
    total_amount=45000.00,
    recipient_key="123.456.789-00",
    method=2,
)

print("✅ Batch Created:")
print(f"Batch ID: {result['batch_id']}")
for i, tx in enumerate(result['pix_transactions'], 1):
    print(f"  Transaction {i}: R${tx['amount']:,.2f} | e2e: {tx['endToEndId']}")

responses = payout_manager.process_batch(result['batch_id'])
print("\n📡 Bank Responses (Simulated):")
for resp in responses:
    print(f"  e2e: {resp['endToEndId']} | Amount: R${resp['payment']['amount']:,.2f}")

webhook_payload = payout_manager.get_batch_details(result['batch_id'])
print("\n📤 Webhook Payload (to send to client):")
print(json.dumps(webhook_payload, indent=2, ensure_ascii=False))
```

---

### **method=1 — linear (4 equal parts)**

```python
import json
payout_manager = BatchPayoutManager()

result = payout_manager.create_batch(
    total_amount=45000.00,
    recipient_key="123.456.789-00",
    method=1,
)

print("✅ Batch Created:")
print(f"Batch ID: {result['batch_id']}")
for i, tx in enumerate(result['pix_transactions'], 1):
    print(f"  Transaction {i}: R${tx['amount']:,.2f} | e2e: {tx['endToEndId']}")

responses = payout_manager.process_batch(result['batch_id'])
print("\n📡 Bank Responses (Simulated):")
for resp in responses:
    print(f"  e2e: {resp['endToEndId']} | Amount: R${resp['payment']['amount']:,.2f}")

webhook_payload = payout_manager.get_batch_details(result['batch_id'])
print("\n📤 Webhook Payload (to send to client):")
print(json.dumps(webhook_payload, indent=2, ensure_ascii=False))
```

---

## 🔒 Legal disclaimer

This repository is a **technical proof of concept**. It is **not** legal or regulatory advice. Do not use it to conceal illicit activity. To operate **above** the per-transaction cap, seek **BCB authorization** and implement **AML/KYC** and **monitoring** controls.

---
