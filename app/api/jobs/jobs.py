from typing import List
from typing import Optional

from app.api.jobs.forms import JobCreateForm
from app.api.jobs.model import create_new_job
from app.api.jobs.model import delete_job_by_id
from app.api.jobs.model import list_jobs
from app.api.jobs.model import retreive_job
from app.api.jobs.model import search_job
from app.api.jobs.model import update_job_by_id
from app.api.users.users import get_current_user_from_token
from app.api.utils import OAuth2PasswordBearerWithCookie
from app.db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .schema import JobCreate
from .schema import ShowJob
from ..users.model import User

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")


@router.post("/create-job/", response_model=ShowJob)
def create_job(
        job: JobCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token)
):
    job = create_new_job(job=job, db=db, owner_id=current_user.id)
    return job


@router.get(
    "/get/{id}", response_model=ShowJob
)  # if we keep just "{id}" . it would stat catching all routes
def read_job(id: int, db: Session = Depends(get_db)):
    job = retreive_job(id=id, db=db)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with this id {id} does not exist",
        )
    return job


@router.get("/all_jobs", response_model=List[ShowJob])
def read_jobs(request: Request, db: Session = Depends(get_db)):
    jobs = list_jobs(db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "jobs": jobs}
    )


@router.get("/my_jobs", response_model=List[ShowJob])
def read_user_jobs(request: Request, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    jobs = list_jobs(db=db, owner_id=current_user.id)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "jobs": jobs}
    )


@router.put("/update/{id}")
def update_job(id: int, job: JobCreate, db: Session = Depends(get_db)):
    current_user = 1
    message = update_job_by_id(id=id, job=job, db=db, owner_id=current_user)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {id} not found"
        )
    return {"msg": "Successfully updated data."}


@router.delete("/delete/{id}")
def delete_job(
        id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
):
    job = retreive_job(id=id, db=db)
    if not job:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {id} does not exist",
        )
    print(job.owner_id, current_user.id, current_user.is_superuser)
    if job.owner_id == current_user.id or current_user.is_superuser:
        delete_job_by_id(id=id, db=db, owner_id=current_user.id)
        return {"detail": "Successfully deleted."}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )


@router.get("/autocomplete")
def autocomplete(term: Optional[str] = None, db: Session = Depends(get_db)):
    jobs = search_job(term, db=db)
    job_titles = []
    for job in jobs:
        job_titles.append(job.title)
    return


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db), msg: str = None):
    jobs = list_jobs(db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "jobs": jobs, "msg": msg}
    )


@router.get("/details/{id}")
def job_detail(id: int, request: Request, db: Session = Depends(get_db)):
    job = retreive_job(id=id, db=db)
    return templates.TemplateResponse(
        "jobs/detail.html", {"request": request, "job": job}
    )


@router.get("/post-a-job/")
def get_create_job(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("jobs/create_job.html", {"request": request})


@router.post("/post-a-job/")
async def create_job(request: Request, db: Session = Depends(get_db)):
    form = JobCreateForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_user: User = get_current_user_from_token(token=param, db=db)
            job = JobCreate(**form.__dict__)
            job = create_new_job(job=job, db=db, owner_id=current_user.id)
            return responses.RedirectResponse(
                f"/details/{job.id}", status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "You might not be logged in, In case problem persists please contact us."
            )
            return templates.TemplateResponse("jobs/create_job.html", form.__dict__)
    return templates.TemplateResponse("jobs/create_job.html", form.__dict__)


@router.get("/delete-job/")
def show_jobs_to_delete(request: Request, db: Session = Depends(get_db)):
    jobs = list_jobs(db=db)
    return templates.TemplateResponse(
        "jobs/show_jobs_to_delete.html", {"request": request, "jobs": jobs}
    )


@router.get("/search/")
def search(
        request: Request, db: Session = Depends(get_db), query: Optional[str] = None
):
    jobs = search_job(query, db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "jobs": jobs}
    )
