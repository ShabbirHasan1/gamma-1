## Parsers
- ### ICICIDirect

```ICICIDirect(methodType: str, methodName(optional): callable) -> Dict```

> **Arguments**
- **methodType : str** - Type of data you wanna parse from ICICIDirect.
- **methodName : callable** _(optional)_ - Method to call everytime it gets new data, useful in streaming data in real-time.
  
> **Return**
- **_msg:_** _Dict_ - If `methodName` is specified it returns an empty dictionary, else it returns a dictionary containing data.

> **Available methods**

- **MI** - Market Insights
- **CA** - Corporate Actions
- **NW** - Market News
- **TI** - Trading Ideas
- **II** - Investing Ideas
- **SP** - Sector Performance

> **Example**
```py
from parsers import ICICIDirect

...
def on_msg(message: Dict):
    print(message)
...

ICICIDirect(methodType="II", method=on_msg)

# If you just want the dictionary containing the data,
# it exposes "msg" to get the results.
res = ICICIDirect(methodType="II")
print(res.msg)
```